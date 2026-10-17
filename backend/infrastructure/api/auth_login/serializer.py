from rest_framework.authtoken.serializers import AuthTokenSerializer


class LoginSerializer(AuthTokenSerializer):
    """Usuario y contraseña del panel."""
