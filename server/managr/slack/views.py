import json
import logging
from urllib.parse import urlencode
import uuid
from datetime import datetime
from managr.api.models import ExpiringTokenAuthentication
from django.db.models import Q
from django.conf import settings
from django.shortcuts import redirect

from rest_framework import (
    permissions,
    status,
    viewsets,
    viewsets,
    mixins,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from managr.slack import constants as slack_const
from managr.slack.helpers import auth as slack_auth
from managr.slack.helpers import requests as slack_requests
from managr.slack.helpers import interactions as slack_interactions
from managr.slack.helpers import block_builders
from managr.slack.helpers.block_sets import get_block_set
from managr.slack.helpers.utils import block_finder, send_to_error_channel, action_with_params
from managr.core.permissions import IsStaff
from managr.core.serializers import UserSerializer
from managr.core.models import User
from managr.api.decorators import slack_api_exceptions
from managr.organization.models import Organization
from managr.core.background import generate_reminder_message
from .models import (
    OrganizationSlackIntegration,
    UserSlackIntegration,
    OrgCustomSlackForm,
    OrgCustomSlackFormInstance,
)
from .serializers import (
    OrgCustomSlackFormSerializer,
    OrgSlackIntegrationWriteSerializer,
    OrgCustomSlackFormInstanceSerializer,
)
from managr.crm.models import ObjectField

logger = logging.getLogger("managr")


class SlackViewSet(
    viewsets.GenericViewSet,
):
    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-oauth-link",
    )
    def get_oauth_link(self, request, *args, **kwargs):
        redirect_uri = request.data.get("redirect_uri", None)
        link_type = request.data.get("link_type", None)
        if redirect_uri is None:
            raise ValidationError("Missing data.redirect_uri")
        if link_type is None:
            raise ValidationError("Missing data.link_type")
        if link_type not in slack_const.OAUTH_LINK_TYPES:
            raise ValidationError("Invalid link type")
        data = {
            "link": slack_auth.OAuthLinkBuilder(request.user, redirect_uri).link_for_type(link_type)
        }
        print(data)
        return Response(data=data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="generate-access-token",
    )
    def generate_access_token(self, request, *args, **kwargs):
        code = request.data.get("code", None)
        redirect_uri = request.data.get("redirect_uri", None)
        if code is None:
            raise ValidationError("Missing data.code")
        if redirect_uri is None:
            raise ValidationError("Missing data.redirect_uri")
        response = slack_requests.request_access_token(code, redirect_uri)
        data = response.json()
        organization = request.user.organization
        team_id = data.get("team", {}).get("id")
        if not team_id:
            raise ValidationError(
                "We hit an issue getting your team id, please try the integration again."
            )

        # NOTE:
        # Only AddToWorkspace yields tokenType == 'bot'.
        # Both AddToWorkspace and UserSignIn yield data.authedUser, and in both cases
        # the user needs to integrate slack.
        # Therefore user slack integration can and should take place regardless.
        is_refresh = False
        if data.get("token_type") == slack_const.TOKEN_TYPE_BOT:
            scope = data.get("scope")
            team_name = data.get("team").get("name")
            team_id = data.get("team").get("id")
            bot_user_id = data.get("bot_user_id")
            access_token = data.get("access_token")
            incoming_webhook = data.get("incoming_webhook")
            enterprise = data.get("enterprise")
            check_for_existing_team_id = OrganizationSlackIntegration.objects.filter(
                team_id=team_id
            ).first()
            if (
                check_for_existing_team_id
                and check_for_existing_team_id.organization.id != organization.id
            ):
                serializer = OrgSlackIntegrationWriteSerializer(
                    data=dict(
                        scope=scope,
                        team_name=team_name,
                        team_id=team_id,
                        bot_user_id=bot_user_id,
                        access_token=access_token,
                        incoming_webhook=incoming_webhook,
                        enterprise=enterprise,
                    ),
                    instance=check_for_existing_team_id,
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                raise ValidationError(
                    "It seems there is already an existing slack integration for this workspace"
                )
            elif (
                check_for_existing_team_id
                and check_for_existing_team_id.organization.id == organization.id
            ):
                is_refresh = True
                serializer = OrgSlackIntegrationWriteSerializer(
                    data=dict(
                        organization=request.user.organization.id,
                        scope=scope,
                        team_name=team_name,
                        team_id=team_id,
                        bot_user_id=bot_user_id,
                        access_token=access_token,
                        incoming_webhook=incoming_webhook,
                        enterprise=enterprise,
                    ),
                    instance=check_for_existing_team_id,
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                serializer = OrgSlackIntegrationWriteSerializer(
                    data=dict(
                        organization=request.user.organization.id,
                        scope=scope,
                        team_name=team_name,
                        team_id=team_id,
                        bot_user_id=bot_user_id,
                        access_token=access_token,
                        incoming_webhook=incoming_webhook,
                        enterprise=enterprise,
                    )
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            if is_refresh:
                return Response(data=UserSerializer(request.user).data, status=status.HTTP_200_OK)

            integration = serializer.instance

            text = f"ManagrAI has successfully connected to your Slack workspace"
        else:
            team_id = data.get("team", {}).get("id")

            if team_id != request.user.organization.slack_integration.team_id:
                raise ValidationError(
                    "You signed into the wrong Slack workspace, please try again."
                )
        slack_id = data.get("authed_user").get("id")
        org = request.user.organization
        if hasattr(org, "slack_integration"):
            if not request.user.has_slack_integration:
                user_slack = UserSlackIntegration.objects.create(
                    user=request.user,
                    slack_id=slack_id,
                    organization_slack=org.slack_integration,
                )
                # get the user's channel
                res = slack_requests.request_user_dm_channel(
                    user_slack.slack_id, org.slack_integration.access_token
                ).json()
                # save Slack Channel ID
                channel = res.get("channel", {}).get("id")
                user_slack.channel = channel
                user_slack.save()
                slack_requests.send_channel_message(
                    user_slack.channel,
                    user_slack.organization_slack.access_token,
                    block_set=[
                        block_builders.simple_section(
                            "ManagrAI successfully connected to your Slack workspace!"
                        )
                    ],
                )
            # return serialized user because client-side needs updated slackRef(s)
        return Response(data=UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="test-channel",
    )
    def test_channel(self, request, *args, **kwargs):
        ## deprecated this will no longer work as we do not have
        """Send a test message in the Organization's default Slack Channel for the Managr app."""
        organization_slack = request.user.organization.slack_integration
        url = organization_slack.incoming_webhook.get("url")

        text = "Testing, testing... 1, 2. Hello, World!"
        slack_requests.send_channel_message(
            organization_slack.incoming_webhook.get("channel_id"),
            organization_slack.access_token,
            text=text,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="create-channel",
    )
    def slack_create_channel(self, request, *args, **kwargs):
        name = request.data.get("name", None)
        organization_slack = request.user.organization.slack_integration
        team_id = organization_slack.team_id
        slack_id = request.user.slack_integration.slack_id
        if organization_slack:
            create_data = slack_requests.create_channel(
                organization_slack.access_token,
                name=name,
                team_id=team_id,
                user=slack_id,
            )
        else:
            create_data = {"ok": False, "response_metadata": {}}
        return Response(status=status.HTTP_200_OK, data=create_data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="list-channels",
    )
    def slack_channels(self, request, *args, **kwargs):
        cursor = request.data.get("cursor")
        organization_slack = request.user.organization.slack_integration
        if organization_slack:
            channels = slack_requests.list_channels(
                organization_slack.access_token,
                cursor=cursor,
                types=["public_channel", "private_channel"],
                limit=100,
            )
        else:
            channels = {"channels": [], "response_metadata": {}}
        return Response(status=status.HTTP_200_OK, data=channels)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="list-user-channels",
    )
    def slack_user_channels(self, request, *args, **kwargs):
        cursor = request.data.get("cursor")
        organization_slack = request.user.organization.slack_integration
        if organization_slack:
            channels = slack_requests.list_user_channels(
                organization_slack.access_token,
                request.user.slack_integration.slack_id,
                cursor=cursor,
                types=["public_channel", "private_channel"],
                limit=100,
            )
        else:
            channels = {"channels": [], "response_metadata": {}}
        return Response(status=status.HTTP_200_OK, data=channels)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="channel-details",
    )
    def slack_channel_details(self, request, *args, **kwargs):
        organization_slack = request.user.organization.slack_integration
        channel_id = request.GET.get("channel_id", None)
        if organization_slack:
            try:
                channel = slack_requests.get_channel_info(
                    organization_slack.access_token, channel_id
                )
            except Exception:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"success": False, "message": "Failed to retreive channel info"},
                )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"success": False, "message": "Couldn't find your Slack account"},
            )
        return Response(status=status.HTTP_200_OK, data=channel)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="list-users",
    )
    def slack_users(self, request, *args, **kwargs):
        cursor = request.data.get("cursor", None)
        organization_slack = request.user.organization.slack_integration
        if organization_slack:
            users = slack_requests.list_users(organization_slack.access_token, cursor=cursor)
            filtered_members = [member for member in users["members"] if member["deleted"] is False]
            users["members"] = filtered_members
        else:
            users = {"users": [], "response_metadata": {}}
        return Response(status=status.HTTP_200_OK, data=users)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update-zoom-channel",
    )
    def update_zoom_channel(self, request, *args, **kwargs):
        slack_id = request.data.get("slack_id")
        if slack_id:
            slack = (
                UserSlackIntegration.objects.filter(slack_id=slack_id)
                .select_related("user")
                .first()
            )
            if not slack:
                return Response(
                    status=status.HTTP_400,
                    data={"success": False, "message": "Couldn't find your Slack account"},
                )
        slack.zoom_channel = request.data.get("zoom_channel")
        slack.save()
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="update-recap-channel",
    )
    def update_recap_channel(self, request, *args, **kwargs):
        logger.info(f"UPDATE RECAP CHANNEL DATA: {request.data}")
        recap_channel = request.data.get("recap_channel")
        slack_id = request.data.get("slack_id")
        if slack_id:
            slack = (
                UserSlackIntegration.objects.filter(slack_id=slack_id)
                .select_related("user")
                .first()
            )
            if not slack:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"success": False, "message": "Couldn't find your Slack account"},
                )
        if not slack.recap_channel or slack.recap_channel != recap_channel:
            slack.change_recap_channel(recap_channel)
        if request.data.get("users", None):
            for user in request.data.get("users"):
                user_acc = User.objects.filter(id=user).first()
                if user_acc and hasattr(user_acc, "slack_integration"):
                    if slack_id not in user_acc.slack_integration.recap_receivers:
                        user_acc.slack_integration.recap_receivers.append(slack_id)
                        user_acc.slack_integration.save()
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="test-dm",
    )
    def test_DM(self, request, *args, **kwargs):
        """Send a test direct message for the requesting user."""
        user = request.user
        user_slack = user.slack_integration
        access_token = user.organization.slack_integration.access_token

        if not user_slack.channel:
            # request the Slack Channel ID to DM this user
            response = slack_requests.request_user_dm_channel(
                user_slack.slack_id, access_token
            ).json()
            # save Slack Channel ID
            channel = response.get("channel").get("id")
            user_slack.channel = channel
            user_slack.save()

        # DM user
        if not user_slack.is_onboarded:
            slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                text="Welcome to Managr!",
                block_set=get_block_set("onboarding_interaction", {"u": str(user.id)}),
            )

            user_slack.is_onboarded = True
            user_slack.save()

        # NOTE: For DEV_PURPOSES: swap below requests to trigger the initial zoom_meeting UI in a DM
        else:
            slack_requests.send_channel_message(
                user_slack.channel, access_token, text="Hello Friend!"
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["post"],
        permission_classes=[],
        authentication_classes=(slack_auth.SlackWebhookAuthentication,),
        detail=False,
        url_path="interactive-endpoint",
    )
    def interactive_endpoint(self, request):
        """
        Open webhook for the SlackAPI to send data when users
        interact with our Slack App's interface.

        The body of that request will contain a JSON payload parameter.
        Will have a TYPE field that is used to handle request accordingly.
        """
        payload = json.loads(request.data.get("payload"))
        process_output = slack_interactions.handle_interaction(payload)
        return Response(status=status.HTTP_200_OK, data=process_output)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="revoke",
    )
    def revoke(self, request):
        """Revoke the requesting user's Slack authentication tokens."""
        user = request.user
        organization = request.user.organization
        if user.is_admin and hasattr(organization, "slack_integration"):
            slack_int = organization.slack_integration
            r = slack_requests.revoke_access_token(slack_int.access_token)
            slack_int.delete()
        else:
            if hasattr(user, "slack_integration"):
                user.slack_integration.delete()

        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["get", "post"],
        # TODO: Add has sales manager permission
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="org-custom-forms",
    )
    def org_custom_form(self, request):
        """Create, Retrieve, or Update the Org's custom Slack form"""
        # Handle POST
        if request.method == "POST":
            return self._post_org_custom_form(request)

        # Otherwise, handle a GET
        organization = request.user.organization
        # Retrieve the custom slack form and serialize it
        try:
            serializer = OrgCustomSlackFormSerializer(instance=organization.custom_slack_form)
        except OrgCustomSlackForm.DoesNotExist:
            # Raise a NotFound if a custom Slack form hasn't been created yet
            raise NotFound(
                detail="A custom Slack form for your organization does not exist yet.", code=404
            )

        return Response(serializer.data)

    def _post_org_custom_form(self, request):
        """Handle POST action of the custom Slack form endpoint."""
        organization = request.user.organization

        logger.info("REQUEST.DATA:", request.data)
        # Make updates - get or create custom_slack_form
        try:
            instance = organization.custom_slack_form
        except OrgCustomSlackForm.DoesNotExist:
            # Create a new custom Slack form from the POST data, if one doesn't exist yet
            instance = OrgCustomSlackForm.objects.create(organization=organization)

        # Validate incoming POST data
        serializer = OrgCustomSlackFormSerializer(
            data=request.data, instance=instance, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class SlackFormsViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    filterset_fields = [
        "resource",
    ]
    serializer_class = OrgCustomSlackFormSerializer

    def get_queryset(self):
        return OrgCustomSlackForm.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        data = self.request.data
        fields = data.pop("fields", [])
        fields_ref = data.pop("fields_ref", [])
        if not len(data.get("custom_object")):
            data["custom_object"] = None
        data.update(
            {"organization": self.request.user.organization_id, "team": self.request.user.team.id}
        )
        form = OrgCustomSlackForm.objects.filter(
            Q(
                resource=data.get("resource"),
                custom_object=data["custom_object"],
                stage=data.get("stage"),
            )
        ).first()
        if form:
            serializer = self.get_serializer(instance=form, data=data)
        else:
            serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = serializer.instance
        instance.custom_fields.clear()
        fields_state = {}
        for i, field in enumerate(fields_ref):
            instance.custom_fields.add(field["id"], through_defaults={"order": i})
            fields_state[i] = field["apiName"]
        instance.config = fields_state
        instance.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        data = self.request.data
        fields = data.pop("fields", [])
        fields_ref = data.pop("fields_ref", [])
        if not len(data.get("custom_object")):
            data["custom_object"] = None
        data.update(
            {"organization": self.request.user.organization_id, "team": self.request.user.team.id}
        )
        serializer = self.get_serializer(data=data, instance=self.get_object())
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.exception(f"Failed to validate form info for and update due to <{e}>")
        serializer.save()
        instance = serializer.instance
        instance.custom_fields.clear()
        fields_state = {}
        for i, field in enumerate(fields_ref):
            instance.custom_fields.add(
                field["id"],
                through_defaults={"order": i, "include_in_recap": field["includeInRecap"]},
            )
            fields_state[i] = field["apiName"]

        instance.config = fields_state
        instance.save()
        if data["resource"] == "OpportunityLineItem":
            org = Organization.objects.get(id=request.data["organization"])
            org.update_has_settings("products")
            form = OrgCustomSlackForm.objects.filter(
                team=self.request.user.team.id,
                resource="OpportunityLineItem",
                form_type="UPDATE",
            ).first()
            update_data = data
            update_data["form_type"] = "UPDATE"
            update_serializer = self.get_serializer(data=update_data, instance=form)
            update_serializer.is_valid(raise_exception=True)
            instance = update_serializer.instance
            instance.custom_fields.clear()
            for i, field in enumerate(fields):
                form.custom_fields.add(field, through_defaults={"order": i})
            instance.config = fields_state
            instance.save()
        return Response(serializer.data)

    @action(
        methods=["GET"],
        permission_classes=(IsStaff,),
        detail=False,
        url_path="admin",
    )
    def admin_forms(self, request, *args, **kwargs):
        """Endpoint to list orgs and tokens for integration accounts"""
        param = request.query_params.get("org_id", None)
        orgs = OrgCustomSlackForm.objects.filter(organization=param)
        serialized = self.get_serializer(orgs, many=True).data
        return Response(serialized)

    @action(
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="form-refresh",
    )
    def form_refresh(self, request, *args, **kwargs):
        """Endpoint to list orgs and tokens for integration accounts"""
        user = request.user
        forms = OrgCustomSlackForm.objects.for_user(user)
        for form in forms:
            form.recreate_form()
        return Response(status=status.HTTP_200_OK)


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(
        data={
            "response_type": "ephemeral",
            "text": "Oh-Ohh an error occured",
        }
    ),
)
def update_resource(request):
    # list of accepted commands for this fake endpoint
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    user = slack.user
    allowed_commands = (
        ["opportunity", "account", "lead", "contact"]
        if user.crm == "SALESFORCE"
        else ["deal", "company", "contact"]
    )

    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = ["opportunity"] if user.crm == "SALESFORCE" else ["deal"]
    resource_type = None

    if len(command_params):
        if command_params[0] not in allowed_commands:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I don't know that : {},only allowed{}".format(
                        command_params[0], allowed_commands
                    ),
                }
            )
        resource_type = command_params[0][0].upper() + command_params[0][1:]

        blocks = get_block_set(
            "update_modal_block_set",
            {"resource_type": resource_type, "u": str(user.id), "type": "command"},
        )
        access_token = user.organization.slack_integration.access_token

        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        trigger_id = request.data.get("trigger_id")

        private_metadata = {
            "original_message_channel": request.data.get("channel_id"),
            "type": "command",
        }

        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
                "title": {"type": "plain_text", "text": f"Update {resource_type}"},
                "blocks": blocks,
                # "submit": {"type": "plain_text", "text": "Update", "emoji": True},
                "private_metadata": json.dumps(private_metadata),
                "external_id": f"update_modal_block_set.{str(uuid.uuid4())}",
            },
        }
        # logger.info(f"BLOCKS FROM UPDATE --{data}")
        slack_requests.generic_request(url, data, access_token=access_token)

        return Response()


# @api_view(["post"])
# @authentication_classes((slack_auth.SlackWebhookAuthentication,))
# @permission_classes([permissions.AllowAny])
# @slack_api_exceptions(
#     return_opt=Response(data={"response_type": "ephemeral", "text": "Oh-Ohh an error occured",}),
# )
# def update_resource(request):
#     slack_id = request.data.get("user_id")
#     if slack_id:
#         slack = (
#             UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
#         )
#         if not slack:
#             return Response(
#                 data={
#                     "response_type": "ephemeral",
#                     "text": "Sorry, I can't find your ManagrAI account",
#                 }
#             )
#     url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
#     user = slack.user
#     access_token = user.organization.slack_integration.access_token
#     trigger_id = request.data.get("trigger_id")
#     context = {"u": str(user.id), "trigger_id": trigger_id}
#     data = {
#         "trigger_id": trigger_id,
#         "view": {
#             "type": "modal",
#             "callback_id": slack_const.COMMAND_FORMS__SUBMIT_CHAT,
#             "title": {"type": "plain_text", "text": "Update CRM"},
#             "blocks": get_block_set("update_command_block_set", context=context),
#             "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
#             "private_metadata": json.dumps(context),
#         },
#     }
#     slack_requests.generic_request(url, data, access_token=access_token)
#     return Response()


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(
        data={
            "response_type": "ephemeral",
            "text": "Oh-Ohh an error occured",
        }
    ),
)
def create_resource(request):
    # list of accepted commands for this fake endpoint
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    user = slack.user
    allowed_commands = (
        ["opportunity", "account", "lead", "contact"]
        if user.crm == "SALESFORCE"
        else ["deal", "company", "contact"]
    )

    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = ["opportunity"] if user.crm == "SALESFORCE" else ["deal"]
    resource_type = None
    if len(command_params):
        if command_params[0] not in allowed_commands:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I don't know that : {},only allowed{}".format(
                        command_params[0], allowed_commands
                    ),
                }
            )
        resource_type = command_params[0][0].upper() + command_params[0][1:]
        template = (
            OrgCustomSlackForm.objects.for_user(user)
            .filter(Q(resource=resource_type, form_type="CREATE"))
            .first()
        )
        slack_form = OrgCustomSlackFormInstance.objects.create(
            template=template,
            user=user,
        )
        if slack_form:
            stage_name = "StageName" if user.crm == "SALESFORCE" else "dealstage"
            context = {
                "resource_type": resource_type,
                "f": str(slack_form.id),
                "u": str(user.id),
                "type": "command",
            }
            blocks = get_block_set(
                "create_modal",
                context,
            )
            try:
                index, block = block_finder(stage_name, blocks)
            except ValueError:
                # did not find the block
                block = None
                pass
            if user.crm == "HUBSPOT" and resource_type == "Deal":
                try:
                    pipeline_index, pipeline_block = block_finder("pipeline", blocks)
                except ValueError:
                    # did not find the block
                    pipeline_index = False
                    pipeline_block = None
                    pass
                if pipeline_block is None:
                    pipeline_field = ObjectField.objects.filter(
                        crm_object="Deal", api_name="pipeline", user=user
                    ).first()
                    if pipeline_field:
                        pipeline_block = pipeline_field.to_slack_field(None, user, "Deal")
                pipeline_block = {
                    **pipeline_block,
                    "accessory": {
                        **pipeline_block["accessory"],
                        "action_id": f"{slack_const.COMMAND_FORMS__PIPELINE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}&field={str(pipeline_field.id)}",
                    },
                }
                if block:
                    if pipeline_index:
                        del blocks[index]
                    else:
                        blocks[index] = pipeline_block
            else:
                if block:
                    block = {
                        **block,
                        "accessory": {
                            **block["accessory"],
                            "action_id": f"{slack_const.COMMAND_FORMS__STAGE_SELECTED}?u={str(user.id)}&f={str(slack_form.id)}",
                        },
                    }
                    blocks = [*blocks[:index], block, *blocks[index + 1 :]]
            access_token = user.organization.slack_integration.access_token

            url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
            trigger_id = request.data.get("trigger_id")

            private_metadata = {
                "original_message_channel": request.data.get("channel_id"),
                **context,
            }

            data = {
                "trigger_id": trigger_id,
                "view": {
                    "type": "modal",
                    "callback_id": slack_const.COMMAND_FORMS__SUBMIT_FORM,
                    "title": {"type": "plain_text", "text": f"Create {resource_type}"},
                    "blocks": blocks,
                    "submit": {"type": "plain_text", "text": "Create", "emoji": True},
                    "private_metadata": json.dumps(private_metadata),
                    "external_id": f"create_modal.{str(uuid.uuid4())}",
                },
            }

            slack_requests.generic_request(url, data, access_token=access_token)
        return Response()


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def meeting_summary(request):
    # list of accepted commands for this fake endpoint
    allowed_commands = [
        "opportunity",
        "account",
    ]
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    user = slack.user
    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = []
    resource_type = None
    if len(command_params):
        if command_params[0] not in allowed_commands:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I don't know that : {},only allowed{}".format(
                        command_params[0], allowed_commands
                    ),
                }
            )
        resource_type = command_params[0][0].upper() + command_params[0][1:]

        blocks = get_block_set(
            "command_meeting_summary", {"resource_type": resource_type, "u": str(user.id)}
        )
        channel = user.slack_integration.channel
        access_token = user.organization.slack_integration.access_token
        slack_requests.send_channel_message(
            channel, access_token, text=f"Select a {resource_type} to update", block_set=blocks
        )
        return Response()


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(
        data={
            "response_type": "ephemeral",
            "text": "Oh-Ohh an error occured",
        }
    ),
)
def create_task(request):

    # list of accepted commands for this fake endpoint
    allowed_commands = ["opportunity", "account", "lead"]
    slack_id = request.data.get("user_id", None)

    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    user = slack.user
    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = []
    resource_type = None
    if len(command_params):
        if command_params[0] not in allowed_commands:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I don't know that : {},only allowed{}".format(
                        command_params[0], allowed_commands
                    ),
                }
            )
        resource_type = command_params[0][0].upper() + command_params[0][1:]
    else:
        resource_type = "Opportunity"
    context = {"resource_type": resource_type, "u": str(user.id)}
    # channel = user.slack_integration.channel
    access_token = user.organization.slack_integration.access_token
    # slack_requests.send_channel_message(
    #    channel, access_token, text=f"Create a task with managr", block_set=blocks
    # )
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = request.data.get("trigger_id")

    private_metadata = {
        "original_message_channel": request.data.get("channel_id"),
    }

    private_metadata.update(context)
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.COMMAND_CREATE_TASK,
            "title": {"type": "plain_text", "text": f"Create a Task"},
            "blocks": get_block_set(
                "create_task_modal",
                context=context,
            ),
            "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
            "private_metadata": json.dumps(private_metadata),
            "external_id": f"create_task_modal.{str(uuid.uuid4())}",
        },
    }

    slack_requests.generic_request(url, data, access_token=access_token)

    return Response()


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(
        data={
            "response_type": "ephemeral",
            "text": "Oh-Ohh an error occured",
        }
    ),
)
def list_tasks(request):
    ## helper to make datetime longform
    def to_date_string(date):
        if not date:
            return "n/a"
        d = datetime.strptime(date, "%Y-%m-%d")
        return d.strftime("%a, %B %d, %Y")

    slack_id = request.data.get("user_id", None)

    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    user = slack.user

    # Pulls tasks from Salesforce
    blocks = get_block_set("tasks_list", {"u": str(user.id)})
    return Response(data={"response_type": "ephemeral", "text": "Your Tasks", "blocks": blocks})


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
def slack_events(request):
    print(request.data)
    if request.data.get("type") == "url_verification":
        return Response(request.data.get("challenge"))
    slack_event = request.data.get("event", None)
    if slack_event:
        slack_id = slack_event.get("user")
        message_key = slack_event.get("message", False)
        bot_check = (
            slack_event.get("message", {}).get("bot_profile", False)
            if message_key
            else slack_event.get("bot_profile", False)
        )
        if bot_check or slack_event.get("sub_type") in ["message_changed"]:
            return Response()
        user = User.objects.filter(slack_integration__slack_id=slack_id).first()
        if not user:
            slack_requests.send_channel_message(
                slack_event["channel"],
                slack_const.BOT_TOKEN,
                block_set=[
                    block_builders.simple_section(
                        f"Looks like you're not a ManagrAI user. Contact your admin to get invited."
                    )
                ],
            )
            return Response()
        elif slack_event.get("type") == "app_home_opened" and slack_event.get("tab") == "messages":
            slack_id = slack_event.get("user")
            user = User.objects.filter(slack_integration__slack_id=slack_id).first()
            if user and user.slack_integration.is_onboarded:
                return Response()
            elif user and not user.slack_integration.is_onboarded:
                slack_requests.send_channel_message(
                    user.slack_integration.channel,
                    user.organization.slack_integration.access_token,
                    text="Welcome to AI!",
                    block_set=[
                        block_builders.simple_section(
                            f"Welcome <@{user.slack_integration.slack_id}> I'm the ManagrAI bot designed to help you automate PR tasks",
                            "mrkdwn",
                        ),
                    ],
                )
                user_slack = user.slack_integration
                user_slack.is_onboarded = True
                user_slack.save()
                return Response()
            else:
                return Response()
        elif slack_event.get("type") == "message":
            slack_requests.send_channel_message(
                slack_event["channel"],
                user.organization.slack_integration.access_token,
                block_set=[
                    block_builders.simple_section(
                        f"Hi there! :wave: I'm ManagrAI, your AI-powered PR assistant.\nTo get a news summary, run this command: /managrai-search\nIf you need further assistance please email us at support@mymanagr.com"
                    )
                ],
            )
            return Response()
        else:
            return Response()
    else:
        return Response()


def redirect_from_slack(request):
    ## this is only for dev, since the redirect url to localhost will not work
    if settings.IN_DEV:
        code = request.GET.get("code", None)
        state = request.GET.get("state")
        q = urlencode({"code": code, "state": state})
        if not code:
            err = {"error": "there was an error"}
            err = urlencode(err)
            return redirect("http://localhost:8080/settings/integrations")
        return redirect(f"http://localhost:8080/settings/integrations?{q}")
    else:
        return redirect("http://localhost:8080/settings/integrations")


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(
        data={
            "response_type": "ephemeral",
            "text": "Oh-Ohh an error occured",
        }
    ),
)
def add_to_cadence(request):
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    user = slack.user
    blocks = get_block_set(
        "select_account",
        {"u": str(user.id), "type": "command"},
    )
    access_token = user.organization.slack_integration.access_token

    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    trigger_id = request.data.get("trigger_id")
    private_metadata = {
        "channel_id": request.data.get("channel_id"),
        "slack_id": request.data.get("user_id"),
        "resource_type": "Account",
    }

    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ADD_TO_CADENCE,
            "title": {"type": "plain_text", "text": "Select Account"},
            "blocks": blocks,
            "private_metadata": json.dumps(private_metadata),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)

    return Response()


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
def schedule_meeting_command(request):
    slack_id = request.data.get("user_id")
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    user = slack.user
    access_token = user.organization.slack_integration.access_token
    trigger_id = request.data.get("trigger_id")
    context = {"u": str(user.id), "type": "command", "slack_id": slack_id}
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.ZOOM_MEETING__SCHEDULE_MEETING,
            "title": {"type": "plain_text", "text": "Zoom Meeting Scheduler"},
            "blocks": get_block_set("schedule_meeting_modal", context=context),
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "private_metadata": json.dumps(context),
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)
    return Response()


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
def get_notes_command(request):
    slack_id = request.data.get("user_id")
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    user = slack.user
    access_token = user.organization.slack_integration.access_token
    trigger_id = request.data.get("trigger_id")
    options = "%".join(["Contact", "Opportunity", "Account"])
    context = {
        "u": str(user.id),
        "slack_id": slack_id,
        "type": "command",
        "options": options,
        "action_id": "GET_NOTES",
    }
    data = {
        "trigger_id": trigger_id,
        "view": {
            "type": "modal",
            "callback_id": slack_const.GET_NOTES,
            "title": {"type": "plain_text", "text": "Choose Record Type"},
            "blocks": get_block_set("pick_resource_modal_block_set", context=context),
            "private_metadata": json.dumps(context),
            "external_id": f"pick_resource_modal_block_set.{str(uuid.uuid4())}",
        },
    }
    slack_requests.generic_request(url, data, access_token=access_token)
    return Response()


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
def launch_search(request):
    slack_id = request.data.get("user_id")
    text = request.data.get("text", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry, I can't find your ManagrAI account",
                }
            )
    url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
    user = slack.user
    access_token = user.organization.slack_integration.access_token
    trigger_id = request.data.get("trigger_id")
    context = {
        "u": str(user.id),
    }
    if text == "help":
        blockset = [
            block_builders.header_block("Search Help:"),
            block_builders.simple_section(
                "The search command lets you find news clips relevent to the terms in the news search field.\nEnter a date range to expand or focus your search (Default is 1 week).\nThe saved search field contains all of the previously saved search in your account.",
                "mrkdwn",
            ),
        ]
        try:
            res = slack_requests.send_channel_message(
                user.slack_integration.channel,
                user.organization.slack_integration.access_token,
                block_set=blockset,
            )
        except Exception as e:
            send_to_error_channel(str(e), user.email, "news summary command")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
    else:
        blockset = "news_summary_blockset"
        data = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "title": {"type": "plain_text", "text": "News"},
                "blocks": get_block_set(blockset, context=context),
                "private_metadata": json.dumps(context),
                "external_id": f"{blockset}.{str(uuid.uuid4())}",
            },
        }
        data["view"]["callback_id"] = slack_const.PROCESS_NEWS_SUMMARY
        data["view"]["submit"] = {
            "type": "plain_text",
            "text": "Submit",
        }
        slack_requests.generic_request(url, data, access_token=access_token)
    return Response()


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes([ExpiringTokenAuthentication])
def send_summary_to_slack(request):
    from managr.comms.tasks import emit_process_news_summary
    import re

    data = request.data.get("data")
    user = request.user
    search = data.get("search")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    summary = data.get("summary")
    channel_id = data.get("channel_id", False)
    cleaned_text = re.sub(r"\[\d+\]", "", summary).replace("<p>", "").replace("</p>", "\n")
    clips = data.get("clips")
    try:
        blocks = [
            block_builders.context_block(f"{search}", "mrkdwn"),
            block_builders.header_block("Answer"),
            block_builders.simple_section(f"{cleaned_text}\n", "mrkdwn", "SUMMARY"),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Ask Follow-Up",
                        "FOLLOWUP",
                        action_id=action_with_params(
                            slack_const.PROCESS_SHOW_REGENERATE_NEWS_SUMMARY_FORM,
                            [f"sd={start_date}", f"ed={end_date}", f"s={search}"],
                        ),
                    )
                ]
            ),
            block_builders.divider_block(),
            block_builders.header_block("Clips:"),
        ]
        end_index = 5 if len(clips) > 5 else len(clips)
        for i in range(0, end_index):
            article = clips[i]
            date = article["publish_date"][:9]
            fixed_date = f"{date[5:7]}/{date[8:]}/{date[0:4]}"
            author = article["author"].replace("_", "") if article["author"] is not None else "N/A"
            article_text = f"{article['source']['name']}\n*{article['title']}*\n<{article['link']}|Read More>\n_{author}_ - {fixed_date}"
            blocks.append(block_builders.simple_section(article_text, "mrkdwn"))
            blocks.append(block_builders.divider_block())
        channel = channel_id if channel_id else user.slack_integration.channel
        slack_res = slack_requests.send_channel_message(
            channel,
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        print(e)
        send_to_error_channel(str(e), user.email, "send summary to slack")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["post"])
@permission_classes([permissions.AllowAny])
@authentication_classes([ExpiringTokenAuthentication])
def send_write_to_slack(request):
    data = request.data
    user = request.user
    pitch = data.get("pitch")
    prompt = data.get("prompt")
    detail_id = data.get("detail_id")
    writing_style_id = data.get("writing_style_id")
    channel_id = data.get("channel_id", False)
    params = [f"u={str(user.id)}"]
    if detail_id:
        params.append(f"d={detail_id}")
    if writing_style_id:
        params.append(f"ws={writing_style_id}")
    try:
        blocks = [
            block_builders.context_block(f"{prompt}", "mrkdwn"),
            block_builders.header_block("Answer:"),
            block_builders.simple_section(f"{pitch}\n", "mrkdwn", "PITCH"),
            block_builders.actions_block(
                [
                    block_builders.simple_button_block(
                        "Make Edits",
                        "EDIT",
                        action_id=action_with_params(
                            slack_const.PROCESS_ADD_EDIT_FIELD,
                            params,
                        ),
                    )
                ]
            ),
        ]
        channel = channel_id if channel_id else user.slack_integration.channel
        slack_res = slack_requests.send_channel_message(
            channel,
            user.organization.slack_integration.access_token,
            block_set=blocks,
        )
    except Exception as e:
        print(e)
        send_to_error_channel(str(e), user.email, "send summary to slack")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
    return Response(status=status.HTTP_204_NO_CONTENT)


class SlackFormInstanceViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = OrgCustomSlackFormInstanceSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrgCustomSlackFormInstance.objects.all()[:50]
        return OrgCustomSlackFormInstance.objects.filter(
            user__organization=self.request.user.organization
        )

    @action(
        methods=["GET"],
        permission_classes=(IsStaff,),
        detail=False,
        url_path="admin",
    )
    def admin_form_instances(self, request, *args, **kwargs):
        """Endpoint to list orgs and tokens for integration accounts"""
        param = request.query_params.get("org_id", None)
        orgs = OrgCustomSlackFormInstance.objects.filter(user__organization=param)[:50]
        serialized = self.get_serializer(orgs, many=True).data
        return Response(serialized)
