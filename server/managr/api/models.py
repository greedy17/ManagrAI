from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


class ManagrToken(Token):
    expiration = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=7))
    is_revoked = models.BooleanField(default=False)

    def refresh(self):
        self.expiration = timezone.now() + timezone.timedelta(days=7)
        self.is_revoked = False
        self.save()

    def revoke(self):
        self.is_revoked = True
        self.save()


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = ManagrToken.objects.get(key=key)
        except ManagrToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")
        if token.is_revoked:
            raise AuthenticationFailed("Token has been revoked")
        if token.expiration < timezone.now():
            raise AuthenticationFailed("Token has expired")

        return (token.user, token)

