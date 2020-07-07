import requests
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from django.db import transaction
from django.template.exceptions import TemplateDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import authenticate, login

from managr.core.nylas.auth import get_access_token, get_account_details

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
from rest_framework import viewsets, mixins, generics, status, filters, permissions
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import (
    User,
    ACCOUNT_TYPE_MANAGER,
    STATE_ACTIVE,
    STATE_INVITED,
    EmailAuthAccount,
    EmailTemplate,
)
from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserInvitationSerializer,
    EmailTemplateSerializer,
    EmailSerializer,
)
from .permissions import IsOrganizationManager, IsSuperUser
from managr.organization.models import Organization

from .nylas.emails import (
    send_new_email_legacy,
    retrieve_threads,
    retrieve_messages,
    generate_preview_email_data,
    return_file_id_from_nylas,
    download_file_from_nylas,
)


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
        if self.request.user.is_superuser:
            return User.objects.all()
        elif (
            self.request.user.type == ACCOUNT_TYPE_MANAGER
            and self.request.user.is_active
        ):
            return User.objects.filter(organization=self.request.user.organization)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["pk"])
        request_user = request.user
        serializer = self.serializer_class(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if request_user != user:
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
        serializer = EmailSerializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.send()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
        url_path="preview-email",
    )
    def preview_email(self, request, *args, **kwargs):
        """Render the email based on provided context and return the result."""
        serializer = EmailSerializer(
            data=request.data, context={"request": request})
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
        response = return_file_id_from_nylas(
            user=user, file_object=file_object)

        return Response(response, status=status.HTTP_200_OK)


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
    [permissions.IsAuthenticated, ]
)
# temporarily allowing any, will only allow self in future
def get_email_authorization_link(request):
    """ This endpoint is used to generate a user specific link with a magic token to
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


class NylasMessageWebhook(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """ Respond to Nylas verification webhook """
        challenge = request.query_params.get('challenge', None)
        if challenge:
            return HttpResponse(content=challenge)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        data = request.data
        print(data)
        return Response()


@api_view(["GET"])
# nylas attaches a special header we can check for
@permission_classes([permissions.AllowAny, ])
def respond_to_nylas_verification(request):
    """ Respond to Nylas verification webhook """
    challenge = request.query_params.get('challenge', None)
    if challenge:
        return HttpResponse(content=challenge)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes(
    [permissions.IsAuthenticated, ]
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
        raise ValidationError(
            {"detail": "Code or magic_token parameter missing"})

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
            raise ValidationError(
                {"detail": {"code": "code is a required field"}})
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
    """ endpoint to revoke access for a token
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
            ea = EmailAuthAccount.objects.filter(
                user__is_serviceaccount=True).first()
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
                {"email": response_data["email"],
                    "name": response_data["first_name"]}
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
                """ this error is most likely going to be an error on our set
                up rather than the user_token """
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
