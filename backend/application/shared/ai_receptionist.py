"""La recepcionista con IA (Gemma en local). El modelo propone texto y acción; aquí se valida antes de ejecutar."""

import uuid
from datetime import datetime

from django.conf import settings
from django.utils import timezone

import logging

from application.shared.conversation_context import ACTION_SCHEMA, build_system_prompt
from domain.entities.ai_decision import ACTION_BOOK, ACTION_CANCEL, ACTION_HANDOFF, ACTION_OFFER_SLOTS, AiDecision
from domain.entities.chat_reply import ChatReply
from domain.exceptions import LanguageModelUnavailable
from domain.rules import customer_messages
from domain.rules.intent_detector import claims_false_action, mentions_owner_handoff

logger = logging.getLogger(__name__)
MAX_REPLY_LENGTH = 700
HISTORY_SIZE = 12


def parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def parse_start(value):
    try:
        return timezone.make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M"))
    except (TypeError, ValueError):
        return None


def outcome_of(reply):
    """Qué ha pasado de verdad con la respuesta (para las trazas y la evaluación)."""
    data = [button.data for row in reply.buttons for button in row]
    if reply.appointment_id:
        return "booked"
    if any(item.startswith(("slot:", "move:")) for item in data):
        return "slots"
    if any(item.startswith(("cat:", "svc:")) for item in data):
        return "choose_service"
    return "text"


class AiReceptionist:
    def __init__(self, repositories, language_model_service, actions):
        self.repositories = repositories
        self.language_model_service = language_model_service
        self.actions = actions

    def reply(self, conversation, text):
        """Lanza LanguageModelUnavailable si el modelo no está o responde algo inservible."""
        messages = [{"role": "system", "content": build_system_prompt(self.repositories, conversation)}]
        for message in self.repositories.conversations.last_messages(conversation, HISTORY_SIZE):
            messages.append({"role": message.role, "content": message.text})
        decision = AiDecision.from_dict(self.language_model_service.write_json(messages, ACTION_SCHEMA, temperature=0.6))
        if not decision.reply:
            logger.warning("aura_guard rejected=empty_reply")
            raise LanguageModelUnavailable("Respuesta vacía")
        # Control de la respuesta: si se sale del papel de recepcionista, no se envía
        if len(decision.reply) > MAX_REPLY_LENGTH or "```" in decision.reply:
            logger.warning("aura_guard rejected=too_long_or_code")
            raise LanguageModelUnavailable("Respuesta fuera de lugar (demasiado larga o con código)")

        self.guard = "none"
        reply = self.execute_decision(conversation, text, decision)
        reply.by_ai = True
        logger.info("aura_decision proposed=%s result=%s guard=%s", decision.action or "reply", outcome_of(reply), self.guard)
        return reply

    def execute_decision(self, conversation, text, decision):
        service = self.repositories.services.find_active(parse_uuid(decision.service_id))

        if decision.action == ACTION_OFFER_SLOTS:
            if service is None:
                return ChatReply(decision.reply, self.actions.category_buttons())
            return self.actions.offer_slots(conversation, service, parse_date(decision.date), decision.part_of_day, intro=decision.reply)

        if decision.action == ACTION_BOOK and service:
            start = parse_start(decision.start)
            if start is None:
                self.guard = "invalid_time"
                return self.actions.offer_slots(conversation, service, intro=decision.reply)
            reply = self.actions.book(conversation, service, start, decision.client_name)
            # Si la IA dijo bien la hora, mantenemos su texto (más natural); si no, el nuestro
            if reply.appointment_id and f"{timezone.localtime(start):%H:%M}" in decision.reply:
                reply.text = decision.reply
            return reply

        appointment_id = parse_uuid(decision.appointment_id)
        if decision.action == ACTION_CANCEL and appointment_id:
            appointment = self.actions.find_own_appointment(conversation, appointment_id)
            if appointment is None:
                self.guard = "not_her_appointment"
                return ChatReply(customer_messages.appointment_not_found())
            return self.actions.cancel(conversation, appointment)

        if decision.action == ACTION_HANDOFF or mentions_owner_handoff(decision.reply, settings.BUSINESS["owner"]):
            if decision.action != ACTION_HANDOFF:
                self.guard = "promised_owner"
            return self.actions.handoff(conversation, text, say=decision.reply)

        # Salvaguarda: si dice que ha reservado o anulado sin haberlo hecho, ofrecemos botones de verdad
        if claims_false_action(decision.reply):
            self.guard = "false_claim"
            if service:
                return self.actions.offer_slots(conversation, service, intro=customer_messages.ask_to_book_with_buttons())
            return ChatReply(customer_messages.ask_which_service(), self.actions.category_buttons())
        return ChatReply(decision.reply)
