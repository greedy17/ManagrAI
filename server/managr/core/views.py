from django.shortcuts import render
from django.contrib.auth import authenticate
from django.db import transaction
from django.template.exceptions import TemplateDoesNotExist

from rest_framework import (
    viewsets, mixins, generics, status, filters, permissions
)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, UserLoginSerializer, UserRegistrationSerializer


def index(request):
    try:
        return render(request, 'index.html', {})
    except TemplateDoesNotExist:
        return render(request, 'core/index-placeholder.html', {})


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        """
        Validate user credentials, login, and return serialized user + auth token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # If the serializer is valid, then the email/password combo is valid.
        # Get the user entity, from which we can get (or create) the auth token
        user = authenticate(**serializer.validated_data)
        if user is None:
            raise ValidationError(
                detail='Incorrect email and password combination. Please try again.')

        response_data = UserLoginSerializer.login(user, request)
        return Response(response_data)


# TODO: Add relevant mixins to manipulate users via API
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # TODO: Restrict Permissions appropriately
    authentication_classes = ()
    permission_classes = ()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Endpoint to create/register a new user.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # This calls .create() on serializer
        user = serializer.instance

        # Log-in user and re-serialize response
        response_data = UserLoginSerializer.login(user, request)
        return Response(response_data, status=status.HTTP_201_CREATED)
