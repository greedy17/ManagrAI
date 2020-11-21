import requests

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
import logging
from django.core import serializers
from django.db import transaction
from django.template.exceptions import TemplateDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator

from django.db.models import F, Q, Count

from rest_framework import (
    authentication,
    filters,
    permissions,
    generics,
    mixins,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from managr.utils.numbers import format_phone_number, validate_phone_number

from managr.lead import constants as lead_consts
from managr.lead.models import LeadMessage, Notification, Lead
from managr.lead.background import emit_event as emit_log_event

from managr.organization.models import (
    Organization,
    Contact,
)

from managr.core.twilio.messages import (
    create_new_account,
    list_available_numbers,
    send_message,
    list_messages,
    disconnect_twilio_number,
)
from managr.core.nylas.auth import get_access_token, get_account_details
from managr.core import constants as core_consts
from managr.core.background import emit_event, emit_email_sync_event
from managr.slack.models import UserSlackIntegration

from .models import (
    User,
    EmailAuthAccount,
    EmailTemplate,
    MessageAuthAccount,
    NotificationOption,
    NotificationSelection,
)
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserInvitationSerializer,
    EmailTemplateSerializer,
    EmailSerializer,
    MessageAuthAccountSerializer,
    NotificationOptionSerializer,
    NotificationSelectionSerializer,
)
from .permissions import IsOrganizationManager, IsSuperUser

from .nylas.emails import (
    send_new_email_legacy,
    retrieve_threads,
    retrieve_messages,
    generate_preview_email_data,
    return_file_id_from_nylas,
    download_file_from_nylas,
    send_system_email,
)
from .nylas.models import NylasAccountStatus, NylasAccountStatusList

logger = logging.getLogger("managr")


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
                        (
                            "Incorrect email and password combination. "
                            "Please try again"
                        )
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


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):

    serializer_class = UserSerializer
    filter_fields = ("organization",)

    def get_queryset(self):
        return User.objects.for_user(self.request.user)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        request_user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # if request.data does not include quota/commit/upside,
        # then user should not be able to update another user's data
        if not self._is_kpi_update(request) and request_user != user:
            return Response(
                {"non_field_errors": ("You can only update your own details")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
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
        if (
            request.data.get("quota")
            or request.data.get("commit")
            or request.data.get("upside")
        ):
            return True
        return False

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
        pk = kwargs.get("pk", None)
        if not password or not magic_token or not pk:
            raise ValidationError(
                {"detail": [("A magic token, id, and password are required")]}
            )
        try:
            user = User.objects.get(pk=pk)
            if (
                str(user.magic_token) == str(magic_token)
                and not user.magic_token_expired
                and user.is_invited
            ):
                user.set_password(password)
                user.is_active = True
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
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="threads",
    )
    def threads(self, request, *args, **kwargs):
        """Retrieve all of the user's email threads from the connected Nylas account.

        Supported Query Parameters:
            page (int):        Page of results to retrieve.
            page_size (int):   Size of each page of results.
            to_email (str):    Single email.
            any_email (str):   Comma-separated list of emails.
        """
        user = request.user
        threads = retrieve_threads(user, **request.query_params.dict())
        # check threads for leademail count and append that

        return Response(threads)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="thread-messages",
    )
    def thread_messages(self, request, *args, **kwargs):
        """Retrieve all of a user's messages for a specific thread."""
        user = request.user
        thread_id = request.data.get("threadId", None)
        messages = retrieve_messages(user, thread_id)
        return Response(messages)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="send-email",
    )
    def send_email(self, request, *args, **kwargs):
        """
        Sends an email from the requesting user's email address
        """
        serializer = EmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.send()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="send-text-message",
    )
    def send_text_message(self, request, *args, **kwargs):
        user = request.user
        # check if the user has activated their twilio account
        has_auth_account = (
            user.message_auth_account if user.message_auth_account else None
        )
        if not has_auth_account:
            return Response(
                data="{'non_field_errors': User has not set up twilio}",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get the recipient sent as an array (name, phone ) since we have alt phones will only send to phone_number_1
        recipient_contacts = request.data.get("recipients", [])
        recipient_lead = request.data.get("lead")
        lead = Lead.objects.filter(id=recipient_lead).first()
        if lead is None:
            raise ValidationError(
                data="{'lead':'Lead Not Found'}", status=status.HTTP_400_BAD_REQUEST
            )
        recipients = []
        query = Q()

        # get phone numbers
        for recipient in recipient_contacts:
            phone = recipient.get("phone_number_1", None)
            if phone:
                recipients.append(phone)
                query |= Q(phone_number_1=phone)

        contacts_queryset = lead.linked_contacts.all()
        contacts_object = contacts_queryset.filter(query)
        sender = has_auth_account.phone_number

        body = request.data.get("body", None)
        # twilio does not support sending to multiple at once
        for recipient in recipients:
            # not sending to contacts from query set because one number may be linked to multiple contacts
            # will add try catch TODO:-PB 07/28
            try:
                msg = send_message(
                    body,
                    sender,
                    recipient,
                    has_auth_account.status_callback,
                )
                message_id = msg.sid

                lead_message = LeadMessage.objects.create(
                    created_by=user,
                    lead=lead,
                    message_id=message_id,
                    direction=lead_consts.SENT,
                    body=body,
                    status=lead_consts.MESSAGE_PENDING,
                )
                lead_message.linked_contacts.set(contacts_object)
            except APIException as e:
                return Response(
                    {"detail": {"invalid_phone": recipient}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="preview-email",
    )
    def preview_email(self, request, *args, **kwargs):
        """Render the email based on provided context and return the result."""
        serializer = EmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        preview_data = serializer.preview()
        return Response(preview_data, status=status.HTTP_200_OK)

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
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="create-twilio-account",
    )
    def create_twilio_account(self, request, *args, **kwargs):
        user = request.user
        # check to see if the user already has a twilio account
        message_auth_account = MessageAuthAccount.objects.filter(user=user).first()
        if message_auth_account:
            return Response(
                data={"non_field_errors": "User already has a twilio account"}
            )
        # if not then create the new auth account with the phone number
        data = request.data
        phone_number = data.get("phone_number", None)
        if not phone_number:
            raise ValidationError(detail="phone_number required")

        account = create_new_account(phone_number)
        account["user"] = user.id
        serializer = MessageAuthAccountSerializer(data=account)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="remove-twilio-account",
    )
    def remove_twilio_account(self, request, *args, **kwargs):
        user = request.user
        # check to see if the user already has a twilio account
        message_auth_account = MessageAuthAccount.objects.filter(user=user)

        if not message_auth_account.exists():
            return Response(
                data={
                    "non_field_errors": "User does not have an active messaging account"
                }
            )
        # if not then create the new auth account with the phone number
        phone_id = message_auth_account.first().sid
        try:
            disconnect_twilio_number(phone_id)
        except APIException as e:
            return Response(status.HTTP_400_BAD_REQUEST)

        message_auth_account.delete()
        return Response()


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
                data={"activation_link": user.activation_link},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes(
    [
        permissions.IsAuthenticated,
    ]
)
# temporarily allowing any, will only allow self in future
def get_email_authorization_link(request):
    """This endpoint is used to generate a user specific link with a magic token to
    authorize their accounts on Nylas when the user authenticates we will use
    the magic token to approve the authentication and ensure the user has not
    tried to authenticate an alternate email (from the one they have registered
    with). This endpoint technically can be modified by the user as it is a
    redirect link, using the token as a param will allow us to ensure this url
    was generated by our backend and the appropriate email is included.
    """
    u = request.user
    return Response({"email_auth_link": u.email_auth_link})
    # generate link


class GetFileView(View):
    def get(self, request, file_id):
        """ This endpoint returns a file from nylas using an nylas ID """
        user = request.user
        response = download_file_from_nylas(user=user, file_id=file_id)
        return response


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


class NylasMessageWebhook(APIView):
    permission_classes = (permissions.AllowAny,)
    """
         Nylas will send a special header request we can use to check if
        it has permissions
    """

    def get(self, request):
        """ Respond to Nylas verification webhook """
        challenge = request.query_params.get("challenge", None)
        if challenge:
            return HttpResponse(content=challenge)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        data = request.data
        webhook_object = data["deltas"][0]["object"]
        webhook_type = data["deltas"][0]["type"]
        if webhook_type == "message.created" and webhook_object == "message":
            data_object = data["deltas"][0]["object_data"]
            emit_event(
                data_object["account_id"],
                data_object["attributes"]["thread_id"],
                data["deltas"][0]["date"],
                core_consts.NYLAS_WEBHOOK_TYPE_MSG_CREATED,
            )
        elif (
            webhook_type == core_consts.NYLAS_WEBHOOK_TYPE_MSG_OPENED
            and webhook_object == core_consts.NYLAS_WEBHOOK_OBJECT_METADATA
        ):
            data_object = data["deltas"][0]["object_data"]

            # this message has already been notified we will add a kwargs to check if a notif was sent

            emit_event(
                data_object["account_id"],
                data_object["metadata"]["message_id"],
                data["deltas"][0]["date"],
                core_consts.NYLAS_WEBHOOK_TYPE_MSG_OPENED,
                **{"count": data_object["metadata"]["count"]},
            )

        return Response()


class NylasAccountWebhook(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """ Respond to Nylas verification webhook """
        challenge = request.query_params.get("challenge", None)
        if challenge:
            return HttpResponse(content=challenge)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """this endpoint will have to eventually be handled by a different instance
        unlike the messages endpoint we cannot grab an id and pass it to the async
        we can however track the delta and check the api for that delta or we can save it in the cache

        """
        data = request.data
        deltas = data.get("deltas", [])
        # a list class wrapper around custom NylasAccountStatus class
        nylas_data = NylasAccountStatusList(deltas)
        # calling .values on the NylasAccStatList returns a list of lists using the object keys passed
        values = [
            # details is position 0 in the first entry and 1 is resource_status
            (item[0]["account_id"], item[1])
            for item in nylas_data.values("details", "resource_status")
        ]
        email_accounts = []
        for v in values:
            email_account = EmailAuthAccount.objects.filter(account_id=v[0]).first()
            if email_account:
                if email_account.sync_state != v[1]:
                    email_account.sync_state = v[1]
                    email_accounts.append(email_account)
                    emit_email_sync_event(str(email_account.user.id), v[1])
                # if the account is having problems send an email and a notification
                # we will be removing accounts from our db and from nylas if it has been inactive for 5 days

        EmailAuthAccount.objects.bulk_update(email_accounts, ["sync_state"])

        return Response()


class TwilioMessageWebhook(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """ Respond to Twilio webhook """
        return Response()

    def post(self, request):
        """
        this endpoint is used for the status of messages when they are sent
        twilio will hit this endpoint defined on status_url
        """
        # receive message

        # get key items
        recipient = request.data.get("To", None)
        sender = request.data.get("From", None)
        body = request.data.get("Body", None)
        message_id = request.data.get("MessageSid", None)

        # find the user it is associated with
        u = User.objects.filter(message_auth_account__phone_number=recipient).first()
        # check if it is associated with a contact

        contacts_object = Contact.objects.for_user(u).filter(
            Q(phone_number_1=sender) | Q(phone_number_2=sender)
        )

        leads = u.claimed_leads.filter(linked_contacts__in=contacts_object).distinct()
        # !! NOT SURE WHAT TO DO WITH MESSAGES NOT FROM A CONTACT
        # MAYBE SEND THE MESSAGE TO THE USERS
        # REAL PHONE NUMBER

        # create a LeadMessage object

        if leads.count() > 0:
            for lead in leads:
                lead_message = LeadMessage.objects.create(
                    created_by=u,
                    lead=lead,
                    message_id=message_id,
                    direction=lead_consts.RECEIVED,
                    body=body,
                    status=lead_consts.MESSAGE_DELIVERED,
                )

                lead_message.linked_contacts.set(contacts_object)
                lead_message.save()

                #
                # emit and event with LeadMessage.RECEIVED to create activity log
                emit_log_event(lead_consts.MESSAGE_RECEIVED, u, lead_message)
                # send email of received message
                # TODO: PB when we merge in feature alerts we will check notification settings first

                if u.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_TEXT_RECEIVED,
                    core_consts.NOTIFICATION_TYPE_EMAIL,
                ):

                    message_contacts = [
                        f"{contact.first_name} {sender}" for contact in contacts_object
                    ]
                    contacts_string = ",".join(message_contacts)
                    message = {
                        "subject": f"You received a text from {contacts_string}",
                        "body": body,
                    }
                    recipients = [{"name": u.full_name, "email": u.email}]
                    send_system_email(recipients, message)

                # create the notification with resource id being the leadmessage
                # no need to emit an event for this as the notification has no async actions

                if u.check_notification_enabled_setting(
                    core_consts.NOTIFICATION_OPTION_KEY_OPPORTUNITY_TEXT_RECEIVED,
                    core_consts.NOTIFICATION_TYPE_ALERT,
                ):

                    contacts = [
                        dict(
                            first_name=contact.first_name,
                            last_name=contact.last_name,
                            email=contact.email,
                        )
                        for contact in contacts_object
                    ]
                    Notification.objects.create(
                        notify_at=timezone.now(),
                        title="Message Received",
                        notification_type="MESSAGE",
                        resource_id=str(lead_message.id),
                        user=u,
                        meta={
                            "content": body,
                            "linked_contacts": contacts,
                            "leads": [
                                {"id": str(l.id), "title": l.title} for l in leads
                            ],
                        },
                    )

        return Response()


@api_view(["GET"])
@permission_classes(
    [
        permissions.IsAuthenticated,
    ]
)
def list_available_twilio_numbers(request):
    region = request.query_params.get("region", None)
    numbers = list_available_numbers(region=region)
    return Response(data=numbers)


@api_view(["GET"])
@permission_classes(
    [
        permissions.IsAuthenticated,
    ]
)
def list_twilio_messages(request):

    # get to
    sender = request.query_params.get("sender", None)
    recipient = request.query_params.get("recipient", None)
    if not sender or not recipient:
        raise ValidationError()
    try:
        validate_phone_number(sender)
    except ValueError:
        return Response(
            {"detail": {"invalid_phone": f"{sender} is an invalid phone number"}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        validate_phone_number(recipient)
    except ValueError:
        return Response(
            {"detail": {"invalid_phone": f"{recipient} is an invalid phone number"}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    formatted_sender = format_phone_number(sender, format="+1%d%d%d%d%d%d%d%d%d%d")
    formatted_recipient = format_phone_number(
        recipient, format="+1%d%d%d%d%d%d%d%d%d%d"
    )
    user = request.user
    if user.message_auth_account:
        message_number = user.message_auth_account.phone_number
        if message_number == formatted_sender or message_number == formatted_recipient:
            return Response(data=list_messages(formatted_sender, formatted_recipient))
    # get from
    # make sure one of them is a message auth account
    return Response(
        data={
            "non_field_errors": "User does not have an auth account associated with the phone numebrs provided"
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@permission_classes(
    [
        permissions.AllowAny,
    ]
)
def message_status(request):
    # get the message sid and status
    message_status = request.data.get("MessageStatus", None)
    message_id = request.data.get("MessageSid", None)

    # find the message in the LeadMessage object
    message_obj = LeadMessage.objects.filter(message_id=message_id).first()

    # update its status to Delivered/NotDelivered/
    if not message_status or not message_id:
        raise ValidationError()
    if message_status in lead_consts.MESSAGE_DELIVERED_OPTIONS:
        message_obj.status = lead_consts.MESSAGE_DELIVERED
    if message_status in lead_consts.MESSAGE_NOT_DELIVERED_OPTIONS:
        message_obj.status = lead_consts.MESSAGE_NOT_DELIVERED
    if message_status in lead_consts.MESSAGE_PENDING_OPTIONS:
        message_obj.status = lead_consts.MESSAGE_PENDING
    message_obj.save()

    # emit the event to create the log item only if its status is delivered
    if message_obj and message_status == lead_consts.TWILIO_MESSAGE_DELIVERED:
        emit_log_event(lead_consts.MESSAGE_SENT, message_obj.created_by, message_obj)
    return Response()


@api_view(["POST"])
@permission_classes(
    [
        permissions.IsAuthenticated,
    ]
)
def email_auth_token(request):
    """Nylas OAuth callback.

    NOTE: This is not a Django Rest Framework view, it is a "normal" Django view.

    After authenticating with Google and then authorizing Nylas, the user will be redirected
    to this view. This view will make a "back-channel" to validate the query parameters
    passed along with the client secret.

    If everything checks out, Nylas will return an access_token, which we'll save to the
    EmailAuthAccount model.
    """
    u = request.user

    # if user already has a token revoke it this will make sure we do not have duplicates on Nylas
    # they charge if we have duplicates and there isn't a way to get a list of them
    try:
        u.email_auth_account.revoke()
    except EmailAuthAccount.DoesNotExist:
        # pass here since user does not already have a token to revoke
        pass
    except requests.exceptions.HTTPError as e:
        if 401 in e.args:
            # delete the record so we can create a new link
            u.email_auth_account.delete()
            # we have out of sync data, pass
            # we have a cron job running every 24 hours to remove all old
            # tokens which are not in sync
            pass

    magic_token = request.data.get("magic_token", None)
    code = request.data.get("code", None)

    if not magic_token or not code:
        raise ValidationError({"detail": "Code or magic_token parameter missing"})

    if magic_token == str(u.magic_token) and not u.magic_token_expired:
        # check the user making the request is the same as the one
        # the link was created for
        # note magic tokens are invalid or expired if a user has already authorized or after 30days
        # in this case they will need to re-auth if they already have authorized
        # the token should not be expired before they activate as it should occur
        # once they are re-directed
        if code:
            # ask nylas for user account and create a new model entry
            # returns nylas object that has account and token needed to populate model
            # note nylas error on sdk when code is invalid does not return a proper error,
            # we may need to catch the error as an exception or not use the api sdk
            try:
                access_token = get_access_token(code)
                account = get_account_details(access_token)
                EmailAuthAccount.objects.create(
                    access_token=access_token,
                    account_id=account["account_id"],
                    email_address=account["email_address"],
                    provider=account["provider"],
                    sync_state=account["sync_state"],
                    name=account["name"],
                    linked_at=account["linked_at"],
                    user=request.user,
                )
            except requests.exceptions.HTTPError as e:
                if 400 in e.args:
                    raise ValidationError(
                        {
                            "non_field_errors": {
                                "code": "Code invalid or expired please try again"
                            }
                        }
                    )

        else:
            raise ValidationError({"detail": {"code": "code is a required field"}})
    else:
        return Response(
            data={
                "non_field_errors": "Token Invalid or Expired, please request a new one"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # TODO: Return a redirect to the user's settings page
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
    if request.user.email_auth_account.access_token:
        try:
            request.user.email_auth_account.revoke()
            return Response(status=status.HTTP_200_OK)
        except EmailAuthAccount.DoesNotExist:
            # pass here since user does not already have a token to revoke
            pass
        except requests.exceptions.HTTPError as e:
            if 401 in e.args:
                # delete the record so we can create a new link
                request.user.email_auth_account.delete()
                # we have out of sync data, pass
                # we have a cron job running every 24 hours to remove all old
                #  tokens which are not in sync
                pass
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        raise ValidationError(
            {"non_form_errors": {"no_token": "user has not authorized nylas"}}
        )


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
    permission_classes = (IsSuperUser | IsOrganizationManager,)

    def create(self, request, *args, **kwargs):
        u = request.user

        # in order to invite a user django needs a user to be registered as a service account
        # use server/manage.py createserviceaccount and supply an email
        # for now we will only need one email (ex no-reply@) but in the future we will have more
        # therefore selecting the first email that is of type service_account

        try:
            ea = EmailAuthAccount.objects.filter(user__is_serviceaccount=True).first()
        except EmailAuthAccount.DoesNotExist:
            # currently passing if there is an error, when we are ready we will require this
            pass

        if not u.is_superuser:
            if str(u.organization.id) != str(request.data["organization"]):
                # allow custom organization in request only for SuperUsers
                return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance

        serializer = UserSerializer(user, context={"request": request})
        response_data = serializer.data
        # TODO: PB 05/14/20 sending plain text for now, but will replace with template email
        if ea:
            token = ea.access_token
            sender = {"email": ea.email_address, "name": "Managr"}
            recipient = [
                {"email": response_data["email"], "name": response_data["first_name"]}
            ]
            message = {
                "subject": "Invitation To Join",
                "body": "Your Organization {} has invited you to join Managr, \
                   Please click the following link to accept and activate your account \
                       {}".format(
                    user.organization.name, user.activation_link
                ),
            }
            try:
                send_new_email_legacy(token, sender, recipient, message)
            except Exception as e:
                """this error is most likely going to be an error on our set
                up rather than the user_token"""
                pass
        response_data["activation_link"] = user.activation_link

        return Response(response_data)


class EmailTemplateViewset(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailTemplateSerializer

    def get_queryset(self):
        return EmailTemplate.objects.for_user(self.request.user)


class MessageAuthAccountViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    authentication_class = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MessageAuthAccount

    def get_queryset(self):
        return MessageAuthAccount.objects.filter(user=self.request.user)
