from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.db import transaction
from rest_framework.authtoken.models import Token
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
        elif self.request.user.type == ACCOUNT_TYPE_MANAGER and self.request.user.state == STATE_ACTIVE:
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

    @action(methods=['get'], permission_classes=[IsSuperUser], detail=True, url_path='get_token')
    def magic_token(self, request, *args, **kwargs):
        """
        this is a helper method to get the token for postman requests testing the user activation
        it is currently only open to Super Users but will also allow self in the future
        """
        user = request.user
        res = {}
        if(user.is_superuser):
            try:
                user = User.objects.get(pk=kwargs['pk'])
                res['magic_token'] = user.magic_token
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(res)

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
            user = User.objects.get(pk=kwargs['pk'])
            if str(user.magic_token) == str(magic_token) and not user.magic_token_expired and user.state == STATE_INVITED:
                user.set_password(password)
                user.state = STATE_ACTIVE
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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_account_status(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if user.state == STATE_ACTIVE:
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
