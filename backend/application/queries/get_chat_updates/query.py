from domain.entities import Conversation


class GetChatUpdatesQuery:
    """Mensajes que la dueña ha escrito en un chat web después del último que ya tiene la clienta."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        key = f"{Conversation.WEB_PREFIX}{dto.session}"
        return self.repositories.conversations.owner_messages_after(key, dto.after_message_id)
