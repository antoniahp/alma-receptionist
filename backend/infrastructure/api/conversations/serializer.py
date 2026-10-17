from rest_framework import serializers

from infrastructure.api.shared.serializers import ChatMessageSerializer


class ConversationSerializer(serializers.Serializer):
    key = serializers.CharField(source="conversation.key")
    channel = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(source="conversation.updated_at")
    messages = ChatMessageSerializer(many=True)

    def get_channel(self, item):
        return "Telegram" if item["conversation"].channel == "telegram" else "Web"

    def get_client(self, item):
        client = item["conversation"].client
        return client.name if client else None
