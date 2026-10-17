from rest_framework import serializers


class PushKeysSerializer(serializers.Serializer):
    p256dh = serializers.CharField(max_length=200)
    auth = serializers.CharField(max_length=100)


class PushSubscriptionSerializer(serializers.Serializer):
    """Lo que devuelve el navegador al suscribirse (PushSubscription.toJSON())."""

    endpoint = serializers.URLField(max_length=600)
    keys = PushKeysSerializer()


class PushEndpointSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=600)
