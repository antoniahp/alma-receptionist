"""Acciones que la recepcionista hace igual tanto si responde con IA como con reglas.

Cada acción devuelve un ChatReply listo para enviar a la clienta.
"""

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from application.commands.cancel_appointment.command import CancelAppointmentCommand
from application.commands.cancel_appointment.command_dto import CancelAppointmentCommandDTO
from application.commands.create_help_request.command import CreateHelpRequestCommand
from application.commands.create_help_request.command_dto import CreateHelpRequestCommandDTO
from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from application.queries.get_next_available_slots.query import GetNextAvailableSlotsQuery
from application.queries.get_next_available_slots.query_dto import GetNextAvailableSlotsQueryDTO
from application.queries.get_opening_hours_text.query import GetOpeningHoursTextQuery
from application.queries.get_opening_hours_text.query_dto import GetOpeningHoursTextQueryDTO
from application.queries.get_slots_near.query import GetSlotsNearQuery
from application.queries.get_slots_near.query_dto import GetSlotsNearQueryDTO
from domain.entities import Appointment, Service
from domain.entities.chat_reply import ChatButton, ChatReply
from domain.exceptions import SlotNotAvailable
from domain.rules import customer_messages
from domain.rules import spanish_format as fmt
from domain.rules.intent_detector import normalize_part_of_day
from domain.rules.language import pick, service_name
from domain.rules.text_normalizer import normalize_text

MAX_SLOTS_PER_DAY = 4
SLOT_TIMESTAMP_FORMAT = "%Y%m%d%H%M"


def slot_code(moment):
    return f"{timezone.localtime(moment):{SLOT_TIMESTAMP_FORMAT}}"


class ReceptionistActions:
    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def update_state(self, conversation, **values):
        """Guarda en la conversación en qué punto estamos (qué servicio, si esperamos su nombre...)."""
        conversation.set_state(**values)
        self.repositories.conversations.save(conversation, ["state"])

    def forget_pending(self, conversation):
        """Olvida una reserva o una pregunta a medias: ya no esperamos su móvil ni su nombre."""
        self.update_state(conversation, awaiting=None, pending_service=None, pending_start=None, pending_phone=None, pending_name=None)

    # ---------- botones ----------

    def main_menu_buttons(self):
        return [
            [
                ChatButton(pick("📅 Pedir cita", "📅 Book"), "book"),
                ChatButton(pick("💶 Precios", "💶 Prices"), "prices"),
                ChatButton(pick("🕐 Horario", "🕐 Opening hours"), "hours"),
            ]
        ]

    def category_buttons(self, with_prices=False):
        """Primero se elige categoría: con muchos tratamientos, una lista entera no cabe en el chat.
        'with_prices' solo cuando la clienta ha pedido precios."""
        services = self.repositories.services.list(only_active=True)
        suffix = ":precios" if with_prices else ""
        rows = []
        for key, label in Service.CATEGORIES:
            if any(service.category == key for service in services):
                rows.append([ChatButton(pick(label, Service.CATEGORY_LABELS_EN[key]), f"cat:{key}{suffix}")])
        return rows

    def service_buttons(self, category, with_prices=False):
        rows = []
        for service in self.repositories.services.list(only_active=True):
            if service.category == category:
                label = f"{service_name(service)} · {fmt.euros(service.price)}" if with_prices else service_name(service)
                rows.append([ChatButton(label, f"svc:{service.id}")])
        return rows

    def slot_buttons(self, service, slots, prefix="slot", key=None, with_more=True):
        """Un botón por hora. 'key' es el id de la cita cuando se trata de cambiarla (prefix 'move')."""
        key = key if key is not None else service.id
        rows = [[ChatButton(fmt.button_label(slot), f"{prefix}:{key}:{slot_code(slot)}")] for slot in slots]
        if with_more and slots:
            last_day = timezone.localtime(slots[-1])
            rows.append([ChatButton(pick("Otro día", "Another day"), f"more:{service.id}:{last_day:%Y%m%d}")])
        return rows

    # ---------- información ----------

    def find_service_in_text(self, text):
        """El servicio cuya palabra clave encaja mejor: 'masaje facial' gana a 'facial'."""
        normalized = normalize_text(text)
        best_service = None
        best_length = 0
        for service in self.repositories.services.list(only_active=True):
            for word in service.keyword_list():
                word = normalize_text(word)
                if word and word in normalized and len(word) > best_length:
                    best_service = service
                    best_length = len(word)
        return best_service

    def find_services_in_text(self, text, limit=3):
        """Los tratamientos que nombra un texto, por orden de aparición ("masaje facial o mascarilla antiestrés")."""
        normalized = normalize_text(text)
        found = []
        for service in self.repositories.services.list(only_active=True):
            for name in filter(None, [service.name, service.name_en]):
                start = normalized.find(normalize_text(name))
                if start != -1:
                    found.append((start, start + len(name), service))
        kept = []
        for start, end, service in sorted(found, key=lambda item: item[0] - item[1]):  # los nombres más largos primero
            if all(end <= s or start >= e for s, e, _ in kept) and all(service != other for _, _, other in kept):
                kept.append((start, end, service))
        return [service for _, _, service in sorted(kept, key=lambda item: item[0])][:limit]

    def prices_reply(self):
        return ChatReply(customer_messages.ask_which_category_prices(), self.category_buttons(with_prices=True))

    def category_reply(self, category, with_prices=False):
        services = [service for service in self.repositories.services.list(only_active=True) if service.category == category]
        if not services:
            return ChatReply(customer_messages.ask_which_service(), self.category_buttons())
        if with_prices:
            return ChatReply(customer_messages.prices_text(services), self.service_buttons(category, with_prices=True))
        return ChatReply(customer_messages.ask_which_treatment(), self.service_buttons(category))

    def hours_reply(self):
        hours = GetOpeningHoursTextQuery(self.repositories).execute(GetOpeningHoursTextQueryDTO())
        return ChatReply(f"{hours} {pick('Estamos en', 'We are at')} {settings.BUSINESS['address']}.")

    # ---------- citas ----------

    def offer_slots(self, conversation, service, day=None, part_of_day=None, intro=None, with_price=False):
        """Ofrece huecos: los de un día concreto (y franja) o, si no hay, los próximos."""
        part_of_day = normalize_part_of_day(part_of_day)
        slots = []
        if day:
            slots = GetAvailableSlotsQuery(self.repositories).execute(GetAvailableSlotsQueryDTO(service_id=service.id, day=day))
            if part_of_day == "morning":
                slots = [slot for slot in slots if timezone.localtime(slot).hour < 14]
            if part_of_day == "afternoon":
                slots = [slot for slot in slots if timezone.localtime(slot).hour >= 14]
            if len(slots) > MAX_SLOTS_PER_DAY:
                step = len(slots) / MAX_SLOTS_PER_DAY
                slots = [slots[int(index * step)] for index in range(MAX_SLOTS_PER_DAY)]
        if not slots:
            if day and intro is None:
                intro = customer_messages.day_full_intro(part_of_day)
            slots = GetNextAvailableSlotsQuery(self.repositories).execute(
                GetNextAvailableSlotsQueryDTO(service_id=service.id, count=3, from_day=day)
            )
        if not slots:
            return ChatReply(customer_messages.no_slots_soon(settings.BUSINESS["owner"]))
        self.update_state(conversation, service_id=service.id)
        return ChatReply(intro or customer_messages.offer_slots_intro(service, with_price), self.slot_buttons(service, slots))

    def book(self, conversation, service, start, client_name=None):
        """Reserva para la clienta de la conversación.

        En la web no sabemos quién es: primero le pedimos el móvil (si ya es clienta, la cita va a su ficha)
        y, si es nueva, su nombre. En Telegram ya la conocemos por su chat.
        """
        client = conversation.client
        if client is None:
            phone = conversation.get_state("pending_phone")
            if conversation.channel == "web" and not phone:
                self.update_state(
                    conversation,
                    awaiting="booking_phone",
                    pending_service=service.id,
                    pending_start=slot_code(start),
                    pending_name=client_name,
                )
                return ChatReply(customer_messages.ask_phone_for_booking(start))
            client_name = client_name or conversation.get_state("pending_name")
            if not client_name:
                self.update_state(conversation, awaiting="name", pending_service=service.id, pending_start=slot_code(start))
                return ChatReply(customer_messages.ask_name_for_booking(start))
            client = self.repositories.clients.create(name=client_name.strip().title()[:120], phone=phone or "")
            self.link_client(conversation, client)

        source = Appointment.SOURCE_TELEGRAM if conversation.channel == "telegram" else Appointment.SOURCE_WEB
        try:
            appointment = BookAppointmentCommand(self.repositories, self.message_service).execute(
                BookAppointmentCommandDTO(client_id=client.id, service_id=service.id, start=start, source=source)
            )
        except SlotNotAvailable:
            near = GetSlotsNearQuery(self.repositories).execute(GetSlotsNearQueryDTO(service_id=service.id, wanted=start))
            if not near:
                return ChatReply(customer_messages.slot_taken_no_alternatives(settings.BUSINESS["owner"]))
            return ChatReply(customer_messages.slot_taken(), self.slot_buttons(service, near))

        self.update_state(conversation, awaiting=None, pending_service=None, pending_start=None, pending_phone=None, pending_name=None)
        is_soon = appointment.start - timezone.now() < timedelta(hours=24)
        text = customer_messages.booking_confirmed(client.first_name, service_name(service), appointment.start, is_soon)
        return ChatReply(text, appointment_id=appointment.id)

    def link_client(self, conversation, client):
        """A partir de ahora esta conversación es de esta clienta (su ficha, sus citas)."""
        conversation.client = client
        self.repositories.conversations.save(conversation, ["client"])

    def identify_by_phone(self, conversation, phone):
        """Si el móvil es de una clienta que ya tenemos, une la conversación a su ficha. Devuelve la clienta o None."""
        client = self.repositories.clients.find_by_phone(phone)
        if client:
            self.link_client(conversation, client)
        return client

    def find_own_appointment(self, conversation, appointment_id):
        """Solo puede tocar sus propias citas activas."""
        if conversation.client is None:
            return None
        return self.repositories.appointments.find_active_for_client(appointment_id, conversation.client.id)

    def upcoming_appointments(self, conversation):
        if conversation.client is None:
            return []
        return self.repositories.appointments.list_upcoming_for_client(conversation.client.id, timezone.now())

    def cancel(self, conversation, appointment):
        CancelAppointmentCommand(self.repositories, self.message_service).execute(
            CancelAppointmentCommandDTO(appointment_id=appointment.id, notify_owner=True)
        )
        return ChatReply(
            customer_messages.appointment_cancelled(appointment.start),
            [[ChatButton(pick("Buscar otro día", "Find another day"), f"svc:{appointment.service_id}")]],
        )

    # ---------- pasar a la dueña ----------

    def handoff(self, conversation, question, say=None):
        """Avisa a la dueña y le explica a la clienta qué va a pasar."""
        owner = settings.BUSINESS["owner"]
        already_waiting = self.repositories.help_requests.find_open_for_conversation(conversation) is not None
        help_request = CreateHelpRequestCommand(self.repositories, self.message_service).execute(
            CreateHelpRequestCommandDTO(conversation_id=conversation.id, question=question)
        )
        client_first_name = conversation.client.first_name if conversation.client else ""
        # Si ya estaba esperando respuesta, se añade a lo que se le pasó y no se repite todo el mensaje
        if already_waiting:
            return ChatReply(customer_messages.added_to_question(owner))
        if conversation.channel == "web" and not help_request.contact:
            self.update_state(conversation, awaiting="phone", help_request=help_request.id)
            text = say or customer_messages.handoff_web(owner)
            return ChatReply(f"{text.rstrip()} {customer_messages.handoff_ask_phone()}")
        return ChatReply(say or customer_messages.handoff_telegram(owner, client_first_name))
