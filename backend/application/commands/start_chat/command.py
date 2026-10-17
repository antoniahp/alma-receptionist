from django.conf import settings

from application.shared.receptionist_actions import ReceptionistActions
from domain.entities import ChatMessage, Conversation
from domain.entities.chat_reply import ChatReply
from domain.rules import customer_messages


class StartChatCommand:
    """Saludo inicial de la recepcionista (al abrir el chat web o pulsar Iniciar en Telegram)."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        client = self.repositories.clients.find(dto.client_id)
        conversation = self.repositories.conversations.get_or_create(dto.conversation_key, client)
        actions = ReceptionistActions(self.repositories, self.message_service)
        # Empezar de nuevo (o volver a abrir el chat) no puede dejarla atascada en "dame tu móvil"
        actions.forget_pending(conversation)
        first_name = conversation.client.first_name if conversation.client else ""
        # En la web el aviso de privacidad ya está debajo del chat; en Telegram se lo decimos al saludar
        is_telegram = dto.conversation_key.startswith(Conversation.TELEGRAM_PREFIX)
        privacy_url = f"{settings.PUBLIC_SITE_URL}/privacidad" if is_telegram else ""
        text = customer_messages.greeting(first_name, settings.BUSINESS["assistant_name"], settings.BUSINESS["name"], privacy_url)
        self.repositories.conversations.add_message(conversation, ChatMessage.ASSISTANT, text)
        return ChatReply(text, actions.main_menu_buttons())
