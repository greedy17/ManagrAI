import logging
import requests
import textwrap
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from background_task.models import CompletedTask

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import (
    filters,
    permissions,
    generics,
    mixins,
    status,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from managr.api.emails import send_html_email
from managr.utils import sites as site_utils
from managr.core.utils import pull_usage_data
from managr.slack.helpers import requests as slack_requests, block_builders
from .nylas.auth import get_access_token, get_account_details
from .models import User, NylasAuthAccount, NoteTemplate
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserInvitationSerializer,
    UserRegistrationSerializer,
    NoteTemplateSerializer,
)
from managr.organization.models import Team
from .permissions import IsOrganizationManager, IsSuperUser, IsStaff
from managr.core.background import emit_process_calendar_meetings
from .nylas.emails import (
    send_new_email_legacy,
    return_file_id_from_nylas,
    download_file_from_nylas,
)
from .nylas.models import NylasAccountStatusList

logger = logging.getLogger("managr")


def GET_COMMAND_OBJECTS():
    from managr.salesforce.cron import (
        queue_users_sf_resource,
        queue_users_sf_fields,
    )

    commands = {
        "SALESFORCE_FIELDS": queue_users_sf_fields,
        "SALESFORCE_RESOURCES": queue_users_sf_resource,
        "PULL_USAGE_DATA": pull_usage_data,
    }
    return commands


def index(request):
    try:
        return render(request, "index.html", {})
    except TemplateDoesNotExist:
        return render(request, "core/index-placeholder.html", {})


class UserLoginView(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    For admin login.
    """

    authentication_classes = ()
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """Validate user credentials.

        Return serialized user and auth token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If the serializer is valid, then the email/password combo is valid.
        # Get the user entity, from which we can get (or create) the auth token
        user = authenticate(**serializer.validated_data)
        if user is None:
            raise ValidationError(
                {
                    "non_field_errors": [
                        ("Incorrect email and password combination. " "Please try again")
                    ],
                }
            )
        login(request, user)
        # create token if one does not exist
        Token.objects.get_or_create(user=user)

        # Build and send the response
        u = User.objects.get(pk=user.id)
        serializer = UserSerializer(u, context={"request": request})
        response_data = serializer.data
        response_data["token"] = user.auth_token.key
        return Response(response_data)


class UserRegistrationView(mixins.CreateModelMixin, generics.GenericAPIView):
    """Allow admins to create new user accounts and an organization"""

    authentication_classes = ()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """Validate user credentials.

        Return serialized user and auth token.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance

        # Log in the user server-side and make sure the response includes their
        # token so that they don't have to log in after plugging in their email
        # and password in this step.
        response_data = UserLoginSerializer.login(user, request)
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):

    serializer_class = UserSerializer
    filter_fields = ("organization",)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )

    search_fields = ("first_name", "last_name", "email")

    def get_queryset(self):
        return User.objects.for_user(self.request.user)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # if request.data does not include quota/commit/upside,
        # then user should not be able to update another user's data
        for field in serializer.read_only_fields:
            # remove read_only_fields
            serializer.validated_data.pop(field, None)
        self.perform_update(serializer)
        user = serializer.instance

        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data

        return Response(response_data)

    @action(
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
        detail=True,
        url_path="profile-photo",
    )
    def update_profile_photo(self, request, *args, **kwargs):
        photo = request.data.get("file")
        pk = kwargs.get("pk", None)
        u = User.objects.filter(pk=pk).first()
        if not u:
            raise ValidationError({"user": "invalid user id"})
        u.profile_photo = photo
        u.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _is_kpi_update(self, request):
        if request.data.get("quota") or request.data.get("commit") or request.data.get("upside"):
            return True
        return False

    @action(
        methods=["get"],
        permission_classes=[permissions.AllowAny],
        detail=False,
        url_path="retrieve-email",
    )
    def retrieve_email(self, request, *args, **kwargs):
        """retrieve's a users email to display in field on activation"""
        params = request.query_params
        pk = params.get("id")
        magic_token = params.get("token")

        try:
            user = User.objects.get(pk=pk)
            if str(user.magic_token) == str(magic_token) and user.is_invited:
                if user.is_active:
                    raise ValidationError(
                        {
                            "detail": [
                                (
                                    "It looks like you have already activate your account, click forgot password to reset it"
                                )
                            ]
                        }
                    )
                return Response({"email": user.email, "organization": user.organization.name})

            else:
                return Response(
                    {"non_field_errors": ("Invalid Link or Token")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        detail=True,
        url_path="activate",
    )
    def activate(self, request, *args, **kwargs):
        # users should only be able to activate if they are in an invited state
        magic_token = request.data.get("token", None)
        password = request.data.get("password", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        timezone = request.data.get("timezone", None)
        pk = kwargs.get("pk", None)
        if not password or not magic_token or not pk:
            raise ValidationError({"detail": [("A magic token, id, and password are required")]})
        try:
            user = User.objects.get(pk=pk)
            if str(user.magic_token) == str(magic_token) and user.is_invited:
                if user.is_active:
                    raise ValidationError(
                        {
                            "detail": [
                                (
                                    "It looks like you have already activate your account, click forgot password to reset it"
                                )
                            ]
                        }
                    )
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                user.timezone = timezone
                # expire old magic token and create a new one for other uses
                user.regen_magic_token()
                user.save()
                login(request, user)
                # create token if one does not exist
                Token.objects.get_or_create(user=user)

                # Build and send the response
                serializer = UserSerializer(user, context={"request": request})
                response_data = serializer.data
                response_data["token"] = user.auth_token.key
                return Response(response_data)

            else:
                return Response(
                    {"non_field_errors": ("Invalid Link or Token")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="attach-file",
    )
    def attach_file(self, request, *args, **kwargs):
        """
        Attaches a file and returns file_id
        https://docs.nylas.com/reference#metadata
        """
        user = request.user
        file_object = request.FILES["file"]
        response = return_file_id_from_nylas(user=user, file_object=file_object)

        return Response(response, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsStaff],
        detail=False,
        url_path="staff/commands",
    )
    def launch_command(self, request, *args, **kwargs):
        COMMANDS = GET_COMMAND_OBJECTS()
        data = request.data
        command = data.get("command")
        command_function = COMMANDS[command]
        if command == "SALESFORCE_FIELDS":
            command_function()
            response_data = {
                "success": True,
                "message": "Successfully started field sync for users",
            }
        elif command == "SALESFORCE_RESOURCES":
            command_function()
            response_data = {
                "success": True,
                "message": "Successfully started resource sync for users",
            }
        else:
            # Here
            response_data = {
                "success": True,
                "message": "Successfully started resource sync for users",
                "data": command_function(),
            }
        return Response(data=response_data)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="modify-forecast",
    )
    def modify_forecast(self, request, *args, **kwargs):
        from managr.opportunity.models import Opportunity

        user = request.user
        action = request.data.get("action")
        ids = request.data.get("ids")
        if action == "add":
            for id in ids:
                user.current_forecast.add_to_state(id)
        else:
            for id in ids:
                user.current_forecast.remove_from_state(id)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="get-forecast-values",
    )
    def get_forecast_values(self, request, *args, **kwargs):
        from managr.opportunity.serializers import OpportunitySerializer

        user = request.user
        res = user.current_forecast.get_current_values()
        opps = []
        for item in res:
            serializer = OpportunitySerializer(data=item.as_dict)
            serializer.is_valid()
            opps.append(serializer.data)
        return Response(data=opps, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        # permission_classes=(IsSalesPerson,),
        detail=False,
        url_path="update-user-info",
    )
    def update_user_info(self, request, *args, **kwargs):
        """endpoint to update the Event Calendar ID, the Fake Meeting ID, the Zoom Channel, the Recap Receiver, and the Realtime Alert Config sections"""
        d = request.data
        event_calendar_id = d.get("event_calendar_id")
        fake_meeting_id = d.get("fake_meeting_id")
        zoom_channel = d.get("zoom_channel")
        recap_receivers = d.get("recap_receivers")
        realtime_alert_config = d.get("realtime_alert_config")
        user_id = d.get("user_id")
        user = User.objects.get(id=user_id)
        if user.event_calendar_id != event_calendar_id:
            user.event_calendar_id = event_calendar_id
        if user.fake_meeting_id != fake_meeting_id:
            user.fake_meeting_id = fake_meeting_id
        if user.zoom_channel != zoom_channel:
            user.zoom_channel = zoom_channel
        if user.recap_receivers != recap_receivers:
            user.recap_receivers = recap_receivers
        # Uncomment this when it's working
        # if user.realtime_alert_config != realtime_alert_config:
        #     user.realtime_alert_config = realtime_alert_config
        user.save()
        return Response(data=status.HTTP_200_OK)

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="refresh-calendar-events",
    )
    def refresh_calendar_events(self, request, *args, **kwargs):
        import uuid

        user = self.request.user
        emit_process_calendar_meetings(
            str(user.id), f"calendar-meetings-{user.email}-{str(uuid.uuid4())}"
        )
        return Response(data={"success": True})

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-user",
    )
    def remove_user(self, request, *args, **kwargs):
        remove_id = request.data.get("remove_id")
        try:
            remove_user = User.objects.get(id=remove_id)
            remove_user.is_active = False
            remove_user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Remove user error: {e}")
            return Response(data={"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"], permission_classes=(IsStaff,), detail=False, url_path="admin-tasks",
    )
    def admin_tasks(self, request, *args, **kwargs):
        tasks = CompletedTask.objects.all()[:100]
        dict_tasks = [vars(task) for task in tasks]
        return Response(data={"tasks": dict_tasks})


class ActivationLinkView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None, **kwargs):
        user = None

        try:
            user = User.objects.get(email=kwargs["email"])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user and user.is_active:
            return Response(
                data={"activation_link": user.activation_link}, status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes(
    [permissions.IsAuthenticated,]
)
def get_email_authorization_link(request):
    u = request.user
    return Response({"link": u.email_auth_link})
    # generate link


class GetFileView(View):
    def get(self, request, file_id):
        """This endpoint returns a file from nylas using an nylas ID"""
        user = request.user
        response = download_file_from_nylas(user=user, file_id=file_id)
        return response


"""
TODO 2021-01-15 William: Need to determine whether we still need this viewset.

class NotificationSettingsViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationOptionSerializer

    def get_queryset(self):
        return NotificationOption.objects.for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        # qs = NotificationOption.objects.for_user(request.user)
        qs = self.get_queryset()
        resource_param = request.query_params.get("resource", None)
        if resource_param:
            qs = qs.filter(resource=resource_param)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = NotificationOptionSerializer(
                qs, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = NotificationOptionSerializer(
            qs, many=True, context={"request": request}
        )
        return Response()

    @action(
        methods=["PATCH"],
        permission_classes=(permissions.IsAuthenticated,),
        detail=False,
        url_path="update-settings",
    )
    def update_settings(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        selections = data.get("selections", [])
        for sel in selections:
            selection, created = NotificationSelection.objects.get_or_create(
                option=sel["option"], user=user
            )
            selection.value = sel["value"]
            selection.save()
        return Response()
 """


class NylasAccountWebhook(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """Respond to Nylas verification webhook"""
        challenge = request.query_params.get("challenge", None)
        if challenge:
            return HttpResponse(content=challenge)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        This endpoint will have to eventually be handled by a different instance.
        Unlike the messages endpoint we cannot grab an id and pass it to the async
        we can however track the delta and check the api for that delta or we
        can save it in the cache.
        """
        data = request.data
        deltas = data.get("deltas", [])
        # a list class wrapper around custom NylasAccountStatus class
        nylas_data = NylasAccountStatusList(deltas)
        # calling .values on the NylasAccStatList returns a list of lists using
        # the object keys passed
        values = [
            # details is position 0 in the first entry and 1 is resource_status
            (item[0]["account_id"], item[1])
            for item in nylas_data.values("details", "resource_status")
        ]
        email_accounts = []
        for v in values:
            email_account = NylasAuthAccount.objects.filter(account_id=v[0]).first()
            if email_account:
                if email_account.sync_state != v[1]:
                    email_account.sync_state = v[1]
                    email_accounts.append(email_account)
                    # 2021-01-16 William: The following function is not defined.
                    # emit_email_sync_event(str(email_account.user.id), v[1])
                # if the account is having problems send an email and a notification
                # we will be removing accounts from our db and from nylas if it has
                # been inactive for 5 days

        NylasAuthAccount.objects.bulk_update(email_accounts, ["sync_state"])

        return Response()


@api_view(["POST"])
@permission_classes(
    [permissions.IsAuthenticated,]
)
def email_auth_token(request):
    u = request.user
    print(f"email_auth_token request {request}")
    # if user already has a token revoke it this will make sure we do not have duplicates on Nylas
    try:
        u.nylas.revoke()
    except NylasAuthAccount.DoesNotExist:
        # pass here since user does not already have a token to revoke
        pass
    except requests.exceptions.HTTPError as e:
        if 401 in e.args:
            # delete the record so we can create a new link
            u.nylas.delete()
            # we have out of sync data, pass
            # we have a cron job running every 24 hours to remove all old
            # tokens which are not in sync
            pass

    code = request.data.get("code", None)

    if not code:
        raise ValidationError({"detail": "Code parameter missing"})

    if code:
        # ask nylas for user account and create a new model entry
        # returns nylas object that has account and token needed to populate model
        # note nylas error on sdk when code is invalid does not return a proper error,
        # we may need to catch the error as an exception or not use the api sdk
        try:
            access_token = get_access_token(code)
            details = get_account_details(access_token)

            account = details["account"]
            calendar_data = details["calendars"]
            email_check = [cal for cal in calendar_data if cal["name"] == account["email_address"]]
            calendar = [cal for cal in calendar_data if cal["read_only"] is False]
            if len(email_check):
                calendar_id = email_check[0]["id"]
            else:
                if len(calendar):
                    calendar_id = calendar[0]["id"]
                else:
                    calendar_id = None
            logger.info(
                textwrap.dedent(
                    f"""
                ---------------------------
                NYLAS CALENAR ACCOUNT CREATION INFO: \n
                ----------------------\n
                ACCOUNT INFO: {account}\n
                CALENDAR INFO:{calendar_data}\n
                EMAIL CHECK: {email_check} \n 
                CALENDAR CHECK: {calendar} \n
                FOUND CALENDAR ID: {calendar_id}\n
                -----------------------"""
                )
            )
            NylasAuthAccount.objects.create(
                access_token=access_token,
                account_id=account["account_id"],
                email_address=account["email_address"],
                provider=account["provider"],
                sync_state=account["sync_state"],
                name=account["name"],
                user=request.user,
                event_calendar_id=calendar_id,
            )
        except requests.exceptions.HTTPError as e:
            if 400 in e.args:
                raise ValidationError(
                    {"non_field_errors": {"code": "Code invalid or expired please try again"}}
                )

    else:
        raise ValidationError({"detail": {"code": "code is a required field"}})
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def revoke_access_token(request):
    """endpoint to revoke access for a token
    currently users can only revoke their own access
    if an account needs to revoke someone elses they may
    email the superuser, when we create a list of admins
    for each org they will have access to delete their user's tokens
    alternatively they can set a user to is_active=false and this will
    call the revoke endpoint for the user in an org
    """
    if request.user.nylas.access_token:
        try:
            request.user.nylas.revoke()
            return Response(status=status.HTTP_200_OK)
        except NylasAuthAccount.DoesNotExist:
            # pass here since user does not already have a token to revoke
            pass
        except requests.exceptions.HTTPError as e:
            if 401 in e.args:
                # delete the record so we can create a new link
                request.user.nylas.delete()
                # we have out of sync data, pass
                # we have a cron job running every 24 hours to remove all old
                #  tokens which are not in sync
                pass
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise ValidationError({"non_form_errors": {"no_token": "user has not authorized nylas"}})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_account_status(request):
    """Check whether a User account associated with a given email is active."""
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if user.is_active:
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserInvitationView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserInvitationSerializer
    # permission_classes = (IsSuperUser | IsOrganizationManager,)

    def create(self, request, *args, **kwargs):
        u = request.user
        if not u.is_superuser:
            if str(u.organization.id) != str(request.data["organization"]):
                # allow custom organization in request only for SuperUsers
                return Response(status=status.HTTP_403_FORBIDDEN)
        slack_id = request.data.get("slack_id", False)
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance
        user.organization.add_to_admin_team(user.email)
        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data
        if slack_id:
            text = f"{u.full_name} has invited you to join the Managr! Activate your account here"
            channel_res = slack_requests.request_user_dm_channel(
                slack_id, u.organization.slack_integration.access_token
            ).json()
            channel = channel_res.get("channel", {}).get("id")
            logger.info(f"User {user.id} activation link: {user.activation_link}")
            blocks = [
                block_builders.section_with_button_block(
                    "Register", "register", text, url=user.activation_link
                )
            ]
            if hasattr(u.organization, "slack_integration"):
                slack_requests.send_channel_message(
                    channel,
                    u.organization.slack_integration.access_token,
                    text="You've been invited to Managr!",
                    block_set=blocks,
                )
        return Response(response_data)


class UserPasswordManagmentView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        """endpoint to reset a password that is forgotten"""
        token = request.data.get("token", None)
        if not token:
            raise ValidationError(
                {"detail": {"key": "field_error", "message": "Token is required", "field": "token"}}
            )
        user_id = request.data.get("user_id", None)
        if not user_id:
            raise ValidationError(
                {
                    "detail": {
                        "key": "field_error",
                        "message": "user id is required",
                        "field": "user_id",
                    }
                }
            )
        password = request.data.get("password", None)
        if not password:
            raise ValidationError(
                {
                    "detail": {
                        "key": "field_error",
                        "message": "new password is required",
                        "field": "password",
                    }
                }
            )
        user = User.objects.filter(id=user_id)
        if not user.exists():
            raise ValidationError(
                {
                    "detail": {
                        "key": "not_found",
                        "message": f"User with {user_id} not found in system",
                        "field": "user_id",
                    }
                }
            )
        else:

            user_account = user.first()
            token_valid = default_token_generator.check_token(user_account, token)
            if not token_valid:
                raise ValidationError(
                    {
                        "detail": {
                            "key": "invalid_or_expired_token",
                            "message": "The token is either invalid or expired",
                            "field": "token",
                        }
                    }
                )
            user_account.set_password(password)
            user_account.save()
            UserLoginSerializer.login(user_account, request)

            return Response({"detail": "password successfully reset"})


@api_view(["POST"])
@permission_classes(
    [permissions.AllowAny,]
)
def request_reset_link(request):
    """endpoint to request a password reset email (forgot password)"""
    email = request.data.get("email", None)
    # if no email is provided return validation error
    if email is None:
        raise ValidationError(
            {"detail": {"key": "field_error", "message": "Email Is Required", "field": "email"}}
        )
    # regardless of whether an email exists for a user return a 200 res
    # so that we can avoid phishing attempts
    user = User.objects.filter(email=email)
    if user.exists():
        user_account = user.first()
        context = {
            "site_url": site_utils.get_site_url(),
            "user_id": user_account.id,
            "token": default_token_generator.make_token(user_account),
        }
        subject = render_to_string("registration/password_reset_subject.txt")
        send_html_email(
            subject,
            "registration/password_reset_email.html",
            settings.DEFAULT_FROM_EMAIL,
            [user_account.email],
            context=context,
        )

    return Response({"detail": "password reset email sent"})


@api_view(["GET"])
@permission_classes(
    [permissions.AllowAny,]
)
def get_task_status(request):
    verbose_name = request.GET.get("verbose_name", None)
    if verbose_name:
        try:
            task = CompletedTask.object.get(verbose_name=verbose_name)
            if task:
                data = {"completed": True}
        except CompletedTask.DoesNotExist:
            data = {"completed": False}
    return Response(data=data)


class NoteTemplateViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
):

    serializer_class = NoteTemplateSerializer

    def get_queryset(self):
        return NoteTemplate.objects.for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.request.data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"error": str(e)})
        return Response(status=status.HTTP_200_OK)
