from django.core.exceptions import ValidationError

from domain.entities import ChatMessage, Conversation
from domain.repositories.conversation_repository import ConversationRepository


class DjangoConversationRepository(ConversationRepository):
    def get(self, conversation_id):
        return Conversation.objects.select_related("client").get(pk=conversation_id)

    def get_or_create(self, key, client=None):
        conversation, _ = Conversation.objects.select_related("client").get_or_create(key=key, defaults={"client": client})
        if client and conversation.client_id != client.id:
            conversation.client = client
            conversation.save(update_fields=["client", "updated_at"])
        return conversation

    def save(self, conversation, fields):
        conversation.save(update_fields=list(fields) + ["updated_at"])

    def add_message(self, conversation, role, text, by_ai=False, from_owner=False):
        message = ChatMessage.objects.create(conversation=conversation, role=role, text=text, by_ai=by_ai, from_owner=from_owner)
        conversation.save(update_fields=["updated_at"])
        return message

    def last_messages(self, conversation, limit):
        messages = conversation.messages.order_by("-created_at", "-id")[:limit]
        return list(reversed(list(messages)))

    def list_recent(self, limit):
        # Solo las conversaciones en las que la clienta ha escrito algo (abrir el chat no cuenta)
        conversations = Conversation.objects.filter(messages__role=ChatMessage.USER).distinct()
        return list(conversations.select_related("client").order_by("-updated_at")[:limit])

    def last_message_for_key(self, key):
        return ChatMessage.objects.filter(conversation__key=key).order_by("-created_at", "-id").first()

    def owner_messages_after(self, key, after_message_id=None):
        messages = ChatMessage.objects.filter(conversation__key=key, from_owner=True)
        if after_message_id:
            try:
                last_seen = ChatMessage.objects.filter(pk=after_message_id, conversation__key=key).first()
            except ValidationError:
                last_seen = None
            if last_seen:
                messages = messages.filter(created_at__gt=last_seen.created_at)
        return list(messages.order_by("created_at", "id"))
