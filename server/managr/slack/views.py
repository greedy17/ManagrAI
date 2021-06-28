import json
import logging
from urllib.parse import urlencode
import uuid

from datetime import datetime
from managr.utils import sites as site_utils

from django.db.models import Sum, Avg, Q
from django.conf import settings
from django.shortcuts import redirect

from rest_framework import (
    permissions,
    status,
    viewsets,
    generics,
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
from managr.slack.helpers.utils import (
    action_with_params,
    block_set,
    map_fields_to_type,
    block_finder,
)

from managr.salesforce.models import SalesforceAuthAccountAdapter
from managr.core.serializers import UserSerializer
from managr.core.models import User
from managr.api.decorators import slack_api_exceptions

from .models import (
    OrganizationSlackIntegration,
    UserSlackIntegration,
    OrgCustomSlackForm,
    OrgCustomSlackFormInstance,
)
from .serializers import OrgCustomSlackFormSerializer


from managr.salesforce.routes import routes as model_routes
from managr.slack.helpers.exceptions import (
    UnHandeledBlocksException,
    InvalidBlocksFormatException,
    InvalidBlocksException,
    InvalidAccessToken,
)

logger = logging.getLogger("managr")


class SlackViewSet(viewsets.GenericViewSet,):
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
        # NOTE:
        # Only AddToWorkspace yields tokenType == 'bot'.
        # Both AddToWorkspace and UserSignIn yield data.authedUser, and in both cases
        # the user needs to integrate slack.
        # Therefore user slack integration can and should take place regardless.
        if data.get("token_type") == slack_const.TOKEN_TYPE_BOT:
            scope = data.get("scope")
            team_name = data.get("team").get("name")
            team_id = data.get("team").get("id")
            bot_user_id = data.get("bot_user_id")
            access_token = data.get("access_token")
            incoming_webhook = data.get("incoming_webhook")
            enterprise = data.get("enterprise")
            integration = OrganizationSlackIntegration.objects.create(
                organization=request.user.organization,
                scope=scope,
                team_name=team_name,
                team_id=team_id,
                bot_user_id=bot_user_id,
                access_token=access_token,
                incoming_webhook=incoming_webhook,
                enterprise=enterprise,
            )
            # TODO: Investigate option to not workspace integration pb 04/20/21 Mike ok'd

            text = f"<!here> your organization has connected Managr to your Slack workspace.\nYou can now configure your account by going to the integrations portal here {site_utils.get_site_url()}/settings/integrations"

            channel = integration.incoming_webhook.get("channel_id", None)
            if not channel:
                integration.delete()
                raise ValidationError(
                    {
                        "detail": {
                            "key": "non_field_error",
                            "message": "No Channel Selected, please select a group channel for Managr to connect to",
                            "field": "email",
                        }
                    }
                )
            slack_requests.generic_request(
                integration.incoming_webhook.get("url"), dict(text=text,), integration.access_token,
            )

        else:
            team_id = data.get("team", {}).get("id")
            if not team_id:
                raise ValidationError(
                    "We hit an issue getting your team id, please try the integration again."
                )
            if team_id != request.user.organization.slack_integration.team_id:
                raise ValidationError(
                    "You signed into the wrong Slack workspace, please try again."
                )
        slack_id = data.get("authed_user").get("id")
        org = request.user.organization
        if hasattr(org, "slack_integration"):
            user_slack = UserSlackIntegration.objects.create(
                user=request.user, slack_id=slack_id, organization_slack=org.slack_integration,
            )
            # get the user's channel
            res = slack_requests.request_user_dm_channel(
                user_slack.slack_id, org.slack_integration.access_token
            ).json()
            # save Slack Channel ID
            channel = res.get("channel", {}).get("id")
            user_slack.channel = channel
            user_slack.save()
            if not user_slack.is_onboarded:
                slack_requests.send_channel_message(
                    user_slack.channel,
                    user_slack.user.organization.slack_integration.access_token,
                    text="Welcome to Managr!",
                    block_set=get_block_set(
                        "onboarding_interaction", {"u": str(user_slack.user.id)}
                    ),
                )

                user_slack.is_onboarded = True
                user_slack.save()

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
        url_path="list-public-channels",
    )
    def slack_channels(self, request, *args, **kwargs):
        cursor = request.data.get("cursor")
        organization_slack = request.user.organization.slack_integration
        if organization_slack:
            channels = slack_requests.list_public_channels(
                organization_slack.access_token, cursor=cursor
            )
        else:
            channels = {"channels": [], "response_metadata": {}}
        return Response(status=status.HTTP_200_OK, data=channels)

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

        print("REQUEST.DATA:", request.data)

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
        data.pop("fields_ref", [])
        data.update({"organization": self.request.user.organization_id})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = serializer.instance
        instance.fields.clear()
        for i, field in enumerate(fields):
            instance.fields.add(field, through_defaults={"order": i})

        instance.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):

        data = self.request.data
        fields = data.pop("fields", [])
        fields_ref = data.pop("fields_ref", [])
        data.update({"organization": self.request.user.organization_id})
        serializer = self.get_serializer(data=data, instance=self.get_object())

        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance = serializer.instance
        instance.fields.clear()
        for i, field in enumerate(fields_ref):
            instance.fields.add(
                field["id"],
                through_defaults={"order": i, "include_in_recap": field["includeInRecap"]},
            )
        instance.save()

        return Response(serializer.data)


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(data={"response_type": "ephemeral", "text": "Oh-Ohh an error occured",}),
)
def update_resource(request):
    # list of accepted commands for this fake endpoint
    allowed_commands = ["opportunity", "account", "lead", "contact"]
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I cant find your managr account",
                }
            )
    user = slack.user
    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = ["opportunity"]
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
            "update_modal_block_set", {"resource_type": resource_type, "u": str(user.id)}
        )
        access_token = user.organization.slack_integration.access_token

        url = slack_const.SLACK_API_ROOT + slack_const.VIEWS_OPEN
        trigger_id = request.data.get("trigger_id")

        private_metadata = {
            "original_message_channel": request.data.get("channel_id"),
            "triggered_from": "command",
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
        logger.info(f"BLOCKS FROM UPDATE --{data}")
        slack_requests.generic_request(url, data, access_token=access_token)

        return Response()


@api_view(["post"])
@authentication_classes((slack_auth.SlackWebhookAuthentication,))
@permission_classes([permissions.AllowAny])
@slack_api_exceptions(
    return_opt=Response(data={"response_type": "ephemeral", "text": "Oh-Ohh an error occured",}),
)
def create_resource(request):
    # list of accepted commands for this fake endpoint
    allowed_commands = ["opportunity", "account", "lead", "contact"]
    slack_id = request.data.get("user_id", None)
    if slack_id:
        slack = (
            UserSlackIntegration.objects.filter(slack_id=slack_id).select_related("user").first()
        )
        if not slack:
            return Response(
                data={
                    "response_type": "ephemeral",
                    "text": "Sorry I cant find your managr account",
                }
            )
    user = slack.user
    text = request.data.get("text", "")
    if len(text):
        command_params = text.split(" ")
    else:
        command_params = ["opportunity"]
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
        slack_form = OrgCustomSlackFormInstance.objects.create(template=template, user=user,)
        if slack_form:

            context = {"resource_type": resource_type, "f": str(slack_form.id), "u": str(user.id)}
            blocks = get_block_set("create_modal", context,)
            try:
                index, block = block_finder("StageName", blocks)
            except ValueError:
                # did not find the block
                block = None
                pass

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
                    "text": "Sorry I cant find your managr account",
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
    return_opt=Response(data={"response_type": "ephemeral", "text": "Oh-Ohh an error occured",}),
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
                    "text": "Sorry I cant find your managr account",
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
            "blocks": get_block_set("create_task_modal", context=context,),
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
    return_opt=Response(data={"response_type": "ephemeral", "text": "Oh-Ohh an error occured",}),
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
                    "text": "Sorry I cant find your managr account",
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
    if request.data.get("type") == "url_verification":
        # respond to challenge (should only happen once)
        return Response(request.data.get("challenge"))
    slack_data = request.data
    slack_event = request.data.get("event", None)
    if slack_event:
        if slack_event.get("type") == "app_home_opened" and slack_event.get("tab") == "home":
            slack_id = slack_event.get("user")
            user = User.objects.filter(slack_integration__slack_id=slack_id).first()
            if user and user.is_active:
                slack_requests.publish_view(
                    slack_id,
                    user.organization.slack_integration.access_token,
                    get_block_set("home_modal", {"u": str(user.id)}),
                )
            else:
                # get the user's team and check for the org
                org = OrganizationSlackIntegration.objects.filter(
                    team_id=slack_data.get("team_id")
                ).first()
                # send a generic home page assuming their org has the token
                if org:
                    slack_requests.publish_view(
                        slack_id,
                        org.access_token,
                        get_block_set(
                            "home_modal_generic",
                            {"slack_id": slack_id, "org_name": org.organization.name},
                        ),
                    )
                    return Response()
                else:
                    return Response()
            if user and user.slack_integration.is_onboarded:

                return Response()
            elif user and not user.slack_integration.is_onboarded:
                slack_requests.send_channel_message(
                    user.slack_integration.channel,
                    user.organization.slack_integration.access_token,
                    text="Welcome to Managr!",
                    block_set=get_block_set("onboarding_interaction", {"u": str(user.id)}),
                )
                user_slack = user.slack_integration
                user_slack.is_onboarded = True
                user_slack.save()

                return Response()
            else:
                return Response()
        else:
            return Response()
    else:
        return Response()

        # check if they exist in managr


def redirect_from_slack(request):
    ## this is only for dev, since the redirect url to localhost will not work
    if settings.IN_DEV:
        code = request.GET.get("code", None)
        q = urlencode({"code": code, "state": "SLACK"})
        if not code:
            err = {"error": "there was an error"}
            err = urlencode(err)
            return redirect("http://localhost:8080/settings/integrations")
        return redirect(f"http://localhost:8080/settings/integrations?{q}")
    else:
        return redirect("http://localhost:8080/settings/integrations")
