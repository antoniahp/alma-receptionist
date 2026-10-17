import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from application.commands.save_help_request_contact.command import SaveHelpRequestContactCommand
from application.commands.save_help_request_contact.command_dto import SaveHelpRequestContactCommandDTO
from application.shared.ai_receptionist import AiReceptionist
from application.shared.receptionist_actions import SLOT_TIMESTAMP_FORMAT, ReceptionistActions
from application.shared.rules_receptionist import RulesReceptionist
from domain.entities import ChatMessage
from domain.entities.chat_reply import ChatReply
from domain.exceptions import LanguageModelUnavailable
from domain.rules import customer_messages
from domain.rules import intent_detector as intents
from domain.rules.phone_format import clean_phone
from domain.rules.topic_guard import is_off_topic

logger = logging.getLogger(__name__)
MAX_MESSAGE_LENGTH = 1000


class HandleChatMessageCommand:
    """Una clienta escribe a la recepcionista. Responde la IA local y, si no está, el respaldo por reglas."""

    def __init__(self, repositories, message_service, language_model_service):
        self.repositories = repositories
        self.message_service = message_service
        self.language_model_service = language_model_service
        self.actions = ReceptionistActions(repositories, message_service)

    def execute(self, dto):
        client = self.repositories.clients.find(dto.client_id)
        conversation = self.repositories.conversations.get_or_create(dto.conversation_key, client)
        text = dto.text.strip()[:MAX_MESSAGE_LENGTH]
        if not text:
            return ChatReply(customer_messages.empty_message())

        self.repositories.conversations.add_message(conversation, ChatMessage.USER, text)
        reply = self.reply_to(conversation, text)
        self.repositories.conversations.add_message(conversation, ChatMessage.ASSISTANT, reply.text, by_ai=reply.by_ai)
        return reply

    def reply_to(self, conversation, text):
        # Límites: lo que no tiene que ver con el centro no llega a la IA ni a la dueña
        if is_off_topic(text):
            logger.info("aura_guard forced=off_topic")
            return ChatReply(customer_messages.off_topic(settings.BUSINESS["name"]), self.actions.main_menu_buttons())

        awaiting = conversation.get_state("awaiting")

        if awaiting == "booking_phone" and conversation.client is None:
            return self.reply_with_booking_phone(conversation, text)

        if awaiting == "name" and conversation.client is None:
            reply = self.reply_with_name(conversation, text)
            if reply:
                return reply

        if awaiting == "phone":
            reply = self.reply_with_phone(conversation, text)
            if reply:
                return reply
            self.actions.update_state(conversation, awaiting=None, help_request=None)

        # Salud: lo decide el código, no el modelo. Siempre pasa a la dueña.
        if intents.is_health_question(text):
            logger.info("aura_guard forced=health_handoff")
            return self.actions.handoff(conversation, text, say=customer_messages.health_question(settings.BUSINESS["owner"]))

        try:
            return AiReceptionist(self.repositories, self.language_model_service, self.actions).reply(conversation, text)
        except LanguageModelUnavailable as error:
            # Se ve en la terminal del servidor: así sabemos por qué no ha contestado la IA
            logger.warning("aura_fallback reason=%s", str(error)[:80])
            return RulesReceptionist(self.repositories, self.actions).reply(conversation, text)

    def reply_with_name(self, conversation, text):
        """Estábamos esperando su nombre para cerrar una reserva."""
        name = intents.clean_name(text)
        service, start = self.pending_booking(conversation)
        if not name or service is None:
            return None
        return self.actions.book(conversation, service, start, client_name=name)

    def pending_booking(self, conversation):
        """El tratamiento y la hora que estaba reservando, o (None, None)."""
        service = self.repositories.services.find_active(conversation.get_state("pending_service"))
        pending_start = conversation.get_state("pending_start")
        if service is None or not pending_start:
            return None, None
        return service, timezone.make_aware(datetime.strptime(pending_start, SLOT_TIMESTAMP_FORMAT))

    def reply_with_booking_phone(self, conversation, text):
        """Le pedimos el móvil para guardar la cita en su ficha (o crearle una si es nueva)."""
        phone = intents.extract_phone(text)
        if not phone:
            if intents.is_refusal(text):
                return ChatReply(customer_messages.phone_needed_for_booking(settings.BUSINESS["phone"]))
            return ChatReply(customer_messages.phone_not_understood())
        service, start = self.pending_booking(conversation)
        if service is None:
            self.actions.update_state(conversation, awaiting=None)
            return ChatReply(customer_messages.ask_which_service(), self.actions.category_buttons())
        self.actions.update_state(conversation, pending_phone=clean_phone(phone))
        # Si ya es clienta, la cita va directamente a su ficha; si no, le pedimos el nombre
        self.actions.identify_by_phone(conversation, phone)
        return self.actions.book(conversation, service, start)

    def reply_with_phone(self, conversation, text):
        """Le habíamos pedido un teléfono por si cierra el chat antes de que conteste la dueña."""
        help_request_id = conversation.get_state("help_request")
        phone = intents.extract_phone(text)
        if phone and help_request_id:
            # Si es una clienta que ya tenemos, la conversación (y la pregunta) quedan en su ficha
            if conversation.client is None:
                self.actions.identify_by_phone(conversation, phone)
            SaveHelpRequestContactCommand(self.repositories, self.message_service).execute(
                SaveHelpRequestContactCommandDTO(help_request_id=help_request_id, phone=phone)
            )
            self.actions.update_state(conversation, awaiting=None, help_request=None)
            return ChatReply(customer_messages.phone_saved())
        if intents.is_refusal(text):
            self.actions.update_state(conversation, awaiting=None, help_request=None)
            return ChatReply(customer_messages.phone_refused())
        return None
