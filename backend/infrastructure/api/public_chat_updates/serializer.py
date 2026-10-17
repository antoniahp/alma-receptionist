from rest_framework import serializers


class ChatUpdatesFiltersSerializer(serializers.Serializer):
    session = serializers.UUIDField()
    after = serializers.UUIDField(required=False, allow_null=True, default=None)


class ChatUpdateSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    text = serializers.CharField()
