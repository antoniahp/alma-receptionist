class ListConversationsQuery:
    """Últimas conversaciones con la recepcionista, con sus últimos mensajes."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        result = []
        for conversation in self.repositories.conversations.list_recent(dto.limit):
            messages = self.repositories.conversations.last_messages(conversation, dto.messages_per_conversation)
            result.append({"conversation": conversation, "messages": messages})
        return result
