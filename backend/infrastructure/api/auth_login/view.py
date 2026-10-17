from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructure.api.auth_login.serializer import LoginSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        # La sesión dura PANEL_SESSION_HOURS desde que entra; si la anterior ya caducó, se abre una nueva
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        if token.created < timezone.now() - timedelta(hours=settings.PANEL_SESSION_HOURS):
            token.delete()
            token = Token.objects.create(user=user)
        return Response({"token": token.key})
