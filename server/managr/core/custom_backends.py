from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import BaseBackend


class SSOBackend(BaseBackend):
    def authenticate(self, request, email=None):
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            login(request, user)
            return user
        except User.DoesNotExist:
            return None
