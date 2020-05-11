from django.shortcuts import render
from django.contrib.auth import authenticate, login
import requests
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from managr.core.integrations import get_email_auth_token
from django.template.exceptions import TemplateDoesNotExist
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
from rest_framework import (
    viewsets, mixins, generics, status, filters, permissions
)
from rest_framework.decorators import (api_view, permission_classes, )
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import User, ACCOUNT_TYPE_MANAGER, STATE_ACTIVE, STATE_INVITED
from .serializers import UserSerializer, UserLoginSerializer,  UserInvitationSerializer
from .permissions import (IsOrganizationManager, IsSuperUser)


def index(request):
    try:
        return render(request, 'index.html', {})
    except TemplateDoesNotExist:
        return render(request, 'core/index-placeholder.html', {})


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
            raise ValidationError({
                'non_field_errors': [
                    ('Incorrect email and password combination. '
                     'Please try again')
                ],
            })
        login(request, user)
        # create token if one does not exist
        Token.objects.get_or_create(user=user)

        # Build and send the response
        u = User.objects.get(pk=user.id)
        serializer = UserSerializer(u, context={'request': request})
        response_data = serializer.data
        response_data['token'] = user.auth_token.key
        return Response(response_data)


class UserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin):

    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        elif self.request.user.type == ACCOUNT_TYPE_MANAGER and self.request.user.is_active:
            return User.objects.filter(organization=self.request.user.organization)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        request_user = request.user
        serializer = self.serializer_class(user,
                                           data=request.data,  partial=True)
        serializer.is_valid(raise_exception=True)

        if request_user != user:
            return Response({'non_field_errors': ('You can only update your own details')}, status=status.HTTP_401_UNAUTHORIZED)
        for field in serializer.read_only_fields:
            # remove read_only_fields
            serializer.validated_data.pop(field, None)
        self.perform_update(serializer)
        user = serializer.instance

        serializer = UserSerializer(
            user, context={'request': request})
        response_data = serializer.data

        return Response(response_data)

    @action(methods=['post'], permission_classes=[permissions.AllowAny], detail=True, url_path='activate')
    def activate(self, request, *args, **kwargs):
        # users should only be able to activate if they are in an invited state
        magic_token = request.data.get('token', None)
        password = request.data.get('password', None)
        if not password or not magic_token:
            raise ValidationError({
                'detail': [
                    ('A magic token and id are required')
                ]
            })
        try:
            user = self.get_object()
            if str(user.magic_token) == str(magic_token) and not user.magic_token_expired and user.is_invited:
                user.set_password(password)
                user.is_active = True
                # expire old magic token and create a new one for other uses
                user.regen_magic_token()
                user.save()

                login(request, user)
                # create token if one does not exist
                Token.objects.get_or_create(user=user)

                # Build and send the response
                serializer = UserSerializer(user, context={'request': request})
                response_data = serializer.data
                response_data['token'] = user.auth_token.key
                return Response(response_data)

            else:
                return Response({'non_field_errors': ('Invalid Link or Token')}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ActivationLinkView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None, **kwargs):
        user = None

        try:
            user = User.objects.get(email=kwargs['email'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if user and user.is_active:
            return Response(data={'activation_link': user.activation_link}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, ])
# temporarily allowing any, will only allow self in future
def get_email_authorization_link(request):
    """ this endpoint is used to generate a user specific link with a magic token to authorize their
    accounts on Nylas when the user authenticates we will use the magic token\
    to approve the authentication
    and ensure the user has not tried to authenticate an alternate email (from the one they have registered with).
    This endpoint technically can be modified by the user as it is a redirect link, using the token as a param will allow
    us to ensure this url was generated by our backend and the appropriate email is included.
    """
    u = request.user
    return Response({'email_auth_link': u.email_auth_link})
    # generate link


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
def email_auth_token(request):
    u = request.user
    magic_token = request.data.get('magic_token', None)
    code = request.data.get('code', None)
    if not magic_token or not code:
        raise ValidationError({'detail': 'Code or Magic Token Missing'})
    if magic_token == str(u.magic_token) and not u.magic_token_expired:
        # check the user making the request is the same as the one
        # the link was created for
        # note magic tokens are invalid or expired if a user has already authorized or after 30days
        # in this case they will need to re-auth if they already have authorized
        # the token should not be expired before they activate as it should occur once they are re-directed
        if code:
            # ask nylas for user account and create a new model entry
            # returns nylas object that has account and token needed to populate model
            # note nylas error on sdk when code is invalid does not return a proper error,
            # we may need to catch the error as an exception or not use the api sdk
            print(get_email_auth_token(code))
        else:
            raise ValidationError(
                {'detail': {'code': 'code is a required field'}})
    else:
        return Response(data={'non_field_errors': 'Token Invalid or Expired, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_account_status(request):
    email = request.data.get('email')
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
        user = request.user

        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        if not user.is_superuser:
            if str(user.organization.id) != str(request.data['organization']):
                # allow custom organization in request only for SuperUsers
                return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_create(serializer)
        user = serializer.instance

        serializer = UserSerializer(user, context={'request': request})
        response_data = serializer.data
        # TODO: PB 04/12/20 currently we are returning the link for dev purposes (so that we can test the auth flow) this will be removed when we add a mail service to send the link
        response_data['activation_link'] = user.activation_link

        return Response(response_data)
