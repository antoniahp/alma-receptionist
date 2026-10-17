import uuid
from datetime import datetime, timedelta

from django.utils import timezone

from application.commands.confirm_appointment.command import ConfirmAppointmentCommand
from application.commands.confirm_appointment.command_dto import ConfirmAppointmentCommandDTO
from application.commands.reschedule_appointment.command import RescheduleAppointmentCommand
from application.commands.reschedule_appointment.command_dto import RescheduleAppointmentCommandDTO
from application.queries.get_next_available_slots.query import GetNextAvailableSlotsQuery
from application.queries.get_next_available_slots.query_dto import GetNextAvailableSlotsQueryDTO
from application.queries.get_slots_near.query import GetSlotsNearQuery
from application.queries.get_slots_near.query_dto import GetSlotsNearQueryDTO
from application.shared.receptionist_actions import SLOT_TIMESTAMP_FORMAT, ReceptionistActions
from domain.entities import ChatMessage
from domain.entities.chat_reply import ChatButton, ChatReply
from domain.exceptions import SlotNotAvailable
from domain.rules import customer_messages
from domain.rules.language import pick


def parse_slot(value):
    try:
        return timezone.make_aware(datetime.strptime(value, SLOT_TIMESTAMP_FORMAT))
    except ValueError:
        return None


def parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


class HandleChatButtonCommand:
    """La clienta pulsa un botón del chat. El dato del botón es 'tipo:valor:valor'."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service
        self.actions = ReceptionistActions(repositories, message_service)

    def execute(self, dto):
        client = self.repositories.clients.find(dto.client_id)
        conversation = self.repositories.conversations.get_or_create(dto.conversation_key, client)
        parts = dto.data.split(":")
        kind = parts[0]
        values = parts[1:]

        handlers = {
            "book": self.book_menu,
            "prices": self.prices,
            "hours": self.hours,
            "later": self.later,
            "cat": self.choose_category,
            "svc": self.choose_service,
            "more": self.more_days,
            "slot": self.choose_slot,
            "confirm": self.confirm,
            "change": self.change,
            "move": self.move,
            "cancel": self.cancel,
        }
        handler = handlers.get(kind)
        reply = handler(conversation, values) if handler else ChatReply(customer_messages.button_not_understood())
        self.repositories.conversations.add_message(conversation, ChatMessage.ASSISTANT, reply.text)
        return reply

    def active_service(self, service_id):
        return self.repositories.services.find_active(parse_uuid(service_id))

    def book_menu(self, conversation, values):
        return ChatReply(customer_messages.ask_which_service(), self.actions.category_buttons())

    def choose_category(self, conversation, values):
        category = values[0] if values else ""
        with_prices = len(values) > 1 and values[1] == "precios"
        return self.actions.category_reply(category, with_prices)

    def prices(self, conversation, values):
        return self.actions.prices_reply()

    def hours(self, conversation, values):
        return self.actions.hours_reply()

    def later(self, conversation, values):
        return ChatReply(customer_messages.maybe_later())

    def choose_service(self, conversation, values):
        service = self.active_service(values[0]) if values else None
        if service is None:
            return ChatReply(customer_messages.service_not_available())
        return self.actions.offer_slots(conversation, service)

    def more_days(self, conversation, values):
        if len(values) < 2:
            return ChatReply(customer_messages.button_not_understood())
        service = self.active_service(values[0])
        if service is None:
            return ChatReply(customer_messages.service_not_available())
        try:
            next_day = datetime.strptime(values[1], "%Y%m%d").date() + timedelta(days=1)
        except ValueError:
            next_day = None
        return self.actions.offer_slots(conversation, service, next_day, intro=customer_messages.more_days_intro())

    def choose_slot(self, conversation, values):
        if len(values) < 2:
            return ChatReply(customer_messages.button_not_understood())
        service = self.active_service(values[0])
        start = parse_slot(values[1])
        if service is None or start is None:
            return ChatReply(customer_messages.service_not_available())
        return self.actions.book(conversation, service, start)

    def confirm(self, conversation, values):
        appointment = self.actions.find_own_appointment(conversation, parse_uuid(values[0]) if values else None)
        if appointment is None:
            return ChatReply(customer_messages.appointment_not_found())
        ConfirmAppointmentCommand(self.repositories).execute(ConfirmAppointmentCommandDTO(appointment_id=appointment.id))
        return ChatReply(customer_messages.appointment_confirmed(appointment.client.first_name, appointment.start))

    def change(self, conversation, values):
        appointment = self.actions.find_own_appointment(conversation, parse_uuid(values[0]) if values else None)
        if appointment is None:
            return ChatReply(customer_messages.appointment_not_found())
        slots = GetNextAvailableSlotsQuery(self.repositories).execute(
            GetNextAvailableSlotsQueryDTO(service_id=appointment.service_id, count=3)
        )
        rows = self.actions.slot_buttons(appointment.service, slots, prefix="move", key=appointment.id, with_more=False)
        rows.append([ChatButton(pick("Prefiero anularla", "I’d rather cancel it"), f"cancel:{appointment.id}")])
        return ChatReply(customer_messages.which_new_time(), rows)

    def move(self, conversation, values):
        if len(values) < 2:
            return ChatReply(customer_messages.button_not_understood())
        appointment = self.actions.find_own_appointment(conversation, parse_uuid(values[0]))
        new_start = parse_slot(values[1])
        if appointment is None or new_start is None:
            return ChatReply(customer_messages.appointment_not_found())
        try:
            RescheduleAppointmentCommand(self.repositories, self.message_service).execute(
                RescheduleAppointmentCommandDTO(appointment_id=appointment.id, new_start=new_start)
            )
        except SlotNotAvailable:
            near = GetSlotsNearQuery(self.repositories).execute(
                GetSlotsNearQueryDTO(service_id=appointment.service_id, wanted=new_start, exclude_appointment_id=appointment.id)
            )
            rows = self.actions.slot_buttons(appointment.service, near, prefix="move", key=appointment.id, with_more=False)
            return ChatReply(customer_messages.slot_taken(), rows)
        return ChatReply(customer_messages.appointment_rescheduled(appointment.client.first_name, new_start), appointment_id=appointment.id)

    def cancel(self, conversation, values):
        appointment = self.actions.find_own_appointment(conversation, parse_uuid(values[0]) if values else None)
        if appointment is None:
            return ChatReply(customer_messages.appointment_not_found())
        return self.actions.cancel(conversation, appointment)
