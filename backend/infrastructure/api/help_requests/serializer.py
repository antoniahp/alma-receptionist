from rest_framework import serializers

from infrastructure import dependencies
from infrastructure.api.shared.serializers import ChatMessageSerializer

RECENT_MESSAGES = 6


class HelpRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    client = serializers.UUIDField(source="client_id", allow_null=True)
    client_name = serializers.SerializerMethodField()
    channel = serializers.CharField()
    question = serializers.CharField()
    contact = serializers.CharField()
    status = serializers.CharField()
    answer = serializers.CharField()
    created_at = serializers.DateTimeField()
    answered_at = serializers.DateTimeField(allow_null=True)
    recent = serializers.SerializerMethodField()

    def get_client_name(self, help_request):
        return help_request.client.name if help_request.client else ""

    def get_recent(self, help_request):
        messages = dependencies.get_repositories().conversations.last_messages(help_request.conversation, RECENT_MESSAGES)
        return ChatMessageSerializer(messages, many=True).data
