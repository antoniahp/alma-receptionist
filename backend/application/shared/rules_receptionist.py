"""La recepcionista sin IA: entiende lo básico con reglas y mantiene el mismo tono."""

from django.conf import settings
from django.utils import timezone

from domain.entities.chat_reply import ChatButton, ChatReply
from domain.rules import customer_messages
from domain.rules import intent_detector as intents
from domain.rules import spanish_format as fmt
from domain.rules.language import pick

RECOMMENDED_SERVICE_BY_TOPIC = {"skin": "facial", "relax": "masaje", "event": "fiesta"}


class RulesReceptionist:
    def __init__(self, repositories, actions):
        self.repositories = repositories
        self.actions = actions

    def reply(self, conversation, text):
        owner = settings.BUSINESS["owner"]
        first_name = conversation.client.first_name if conversation.client else ""
        service = self.actions.find_service_in_text(text)
        day = intents.parse_day(text, timezone.localdate())
        part_of_day = intents.parse_part_of_day(text)
        if service is None and (day or part_of_day):
            service = self.service_from_previous_message(conversation)
        intent = intents.detect_intent(text, owner, mentions_service=service is not None, mentions_day=day is not None)

        if intent == intents.ASK_IF_BOT:
            return ChatReply(customer_messages.i_am_virtual_assistant(settings.BUSINESS["name"], owner))

        if intent == intents.TALK_TO_OWNER:
            return self.actions.handoff(conversation, text, say=customer_messages.talk_to_owner(owner, first_name))

        if intent == intents.HEALTH_QUESTION:
            return self.actions.handoff(conversation, text, say=customer_messages.health_question(owner))

        if intent == intents.CHANGE_APPOINTMENT:
            return self.change_appointment_reply(conversation)

        if intent == intents.BOOK:
            if service is None:
                service = self.service_from_previous_message(conversation)
            if service is None:
                return ChatReply(customer_messages.ask_which_service(), self.actions.category_buttons())
            return self.actions.offer_slots(conversation, service, day, part_of_day, with_price=intents.asks_price(text))

        if intent == intents.SERVICE_INFO:
            return ChatReply(
                customer_messages.service_info(service),
                [[ChatButton(pick("📅 Sí, búscame hueco", "📅 Yes, find me a slot"), f"svc:{service.id}")]],
            )

        if intent == intents.PRICES:
            if service:
                return ChatReply(
                    customer_messages.service_price(service),
                    [[ChatButton(pick("📅 Sí, búscame hueco", "📅 Yes, find me a slot"), f"svc:{service.id}")]],
                )
            return self.actions.prices_reply()

        if intent == intents.HOURS:
            return self.actions.hours_reply()

        if intent == intents.RECOMMEND:
            return self.recommendation_reply(text)

        if intent == intents.THANKS:
            return ChatReply(customer_messages.thanks_reply(first_name))

        if intent == intents.GREETING:
            return ChatReply(customer_messages.short_greeting(first_name), self.actions.main_menu_buttons())

        # Una palabra suelta o algo que no es una pregunta: pedimos que lo explique, sin molestar a la dueña
        if not intents.is_question(text):
            return ChatReply(customer_messages.not_understood(), self.actions.main_menu_buttons())

        # Una pregunta que no sabemos contestar: se la pasamos a la dueña
        return self.actions.handoff(conversation, text)

    def service_from_previous_message(self, conversation):
        """Si antes habló de un servicio ('quiero un masaje' ... 'el viernes'), seguimos con ese."""
        return self.repositories.services.find_active(conversation.get_state("service_id"))

    def change_appointment_reply(self, conversation):
        upcoming = self.actions.upcoming_appointments(conversation)
        if not upcoming:
            return ChatReply(customer_messages.no_upcoming_appointments())
        rows = []
        for appointment in upcoming[:3]:
            label = f"{pick('Cambiar', 'Change')} {fmt.day_short(appointment.start)} {fmt.hour(appointment.start)}"
            rows.append([ChatButton(label, f"change:{appointment.id}"), ChatButton(pick("Anular", "Cancel"), f"cancel:{appointment.id}")])
        return ChatReply(customer_messages.what_to_do_with_appointment(), rows)

    def recommendation_reply(self, text):
        topic = intents.recommendation_topic(text)
        keyword = RECOMMENDED_SERVICE_BY_TOPIC.get(topic)
        service = self.actions.find_service_in_text(keyword) if keyword else None
        if service is None:
            return ChatReply(customer_messages.ask_what_they_want())
        return ChatReply(
            customer_messages.recommendation(topic, service),
            [[ChatButton(pick("📅 Sí, búscame hueco", "📅 Yes, find me a slot"), f"svc:{service.id}")]],
        )
