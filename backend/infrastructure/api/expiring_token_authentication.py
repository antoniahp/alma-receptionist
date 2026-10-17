"""El panel guarda datos de salud de las clientas: la sesión caduca y hay que volver a entrar."""

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token.created < timezone.now() - timedelta(hours=settings.PANEL_SESSION_HOURS):
            token.delete()
            raise AuthenticationFailed("La sesión ha caducado. Vuelve a entrar.")
        return user, token
