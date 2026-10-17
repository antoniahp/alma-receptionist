from rest_framework import serializers


class PublicChatSerializer(serializers.Serializer):
    """Una de tres: empezar el chat, pulsar un botón o escribir un mensaje."""

    session = serializers.UUIDField(required=False, allow_null=True)
    start = serializers.BooleanField(required=False, default=False)
    button = serializers.CharField(required=False, max_length=64, allow_blank=True, default="")
    message = serializers.CharField(required=False, max_length=1000, allow_blank=True, default="")
