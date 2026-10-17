from django.conf import settings
from django.utils import timezone

from domain.entities import ChatMessage, HelpRequest
from domain.exceptions import EmptyAnswer, MessageNotSent
from domain.rules import customer_messages


class AnswerHelpRequestCommand:
    """La dueña contesta y la respuesta llega al chat de la clienta (Telegram o web).

    Por defecto sale como un mensaje más de la recepcionista; si se firma, va con el nombre de la dueña.
    """

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        text = dto.text.strip()
        if not text:
            raise EmptyAnswer()
        help_request = self.repositories.help_requests.get(dto.help_request_id)
        message = text
        if dto.sign_as_owner:
            message = customer_messages.signed_by_owner(settings.BUSINESS["owner"], text)

        conversation = help_request.conversation
        if conversation.channel == "telegram":
            if not self.message_service.is_enabled():
                raise MessageNotSent("Telegram no está configurado, así que no se puede enviar la respuesta.")
            self.message_service.send(conversation.telegram_chat_id, message)
        # En la web, el chat de la clienta recoge este mensaje automáticamente en unos segundos
        self.repositories.conversations.add_message(conversation, ChatMessage.ASSISTANT, message, from_owner=True)

        help_request.answer = text
        help_request.status = HelpRequest.ANSWERED
        help_request.answered_at = timezone.now()
        self.repositories.help_requests.save(help_request, ["answer", "status", "answered_at"])
        return help_request
