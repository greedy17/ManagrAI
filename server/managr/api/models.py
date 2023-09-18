from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


def set_expiration():
    return timezone.now() + timezone.timedelta(hours=1)


class ManagrToken(Token):
    expiration = models.DateTimeField(default=set_expiration)
    is_revoked = models.BooleanField(default=False)
    assigned_user = models.OneToOneField(
        User, related_name="access_token", on_delete=models.CASCADE
    )

    def is_expired(self):
        if self.expiration < timezone.now():
            return True
        return False

    @classmethod
    def refresh(cls, token):
        user = token.assigned_user
        token.delete()
        new_token = cls.objects.create(user=user, assigned_user=user)
        return new_token

    def revoke(self):
        self.is_revoked = True
        self.save()


class ExpiringTokenAuthentication(TokenAuthentication):
    keyword = "Token"
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        return ManagrToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _("Invalid token header. Token string should not contain invalid characters.")
            raise AuthenticationFailed(msg)
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = ManagrToken.objects.get(key=key)
        except ManagrToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")
        if token.is_revoked:
            raise AuthenticationFailed("Token has been revoked")
        if token.expiration < timezone.now():
            print(token.assigned_user, token.assigned_user.is_authenticated)
            if token.assigned_user and token.assigned_user.is_authenticated:
                print(vars(token))
                token = ManagrToken.refresh(token)
                print(vars(token))
            else:
                raise AuthenticationFailed("Token has expired")
        return (token.assigned_user, token)

    def authenticate_header(self, request):
        return self.keyword


class EmailBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        try:
            uri = request.build_absolute_uri()
            sso_check = request.data.get("sso")
            if sso_check is None and "login-sso" not in uri:
                return None
            email = request.data.get("email")
        except Exception:
            return None
        return self.authenticate_credentials(email)

    def authenticate_credentials(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("User does not exist")

        return user
