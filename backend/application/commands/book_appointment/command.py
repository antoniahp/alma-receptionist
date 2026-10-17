from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from application.commands.notify_owner.command import NotifyOwnerCommand
from application.commands.notify_owner.command_dto import NotifyOwnerCommandDTO
from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from domain.entities import Appointment
from domain.exceptions import InvalidBookingData, SlotNotAvailable
from domain.rules import customer_messages

# Si la cita es para dentro de menos de esto, la confirmación ya hace de recordatorio
REMINDER_WINDOW = timedelta(hours=24)

SOURCE_LABELS = {Appointment.SOURCE_WEB: "la web", Appointment.SOURCE_TELEGRAM: "Telegram"}


class BookAppointmentCommand:
    """Reserva una cita comprobando que el hueco sigue libre. Avisa a la dueña si la reserva viene de fuera."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        start = timezone.localtime(dto.start)
        client = self.repositories.clients.find(dto.client_id)
        service = self.repositories.services.find_active(dto.service_id)
        if client is None or service is None:
            raise InvalidBookingData()

        with transaction.atomic():
            # Bloqueamos el horario de ese día para que dos reservas a la vez no cojan el mismo hueco
            self.repositories.opening_hours.lock_weekday(start.weekday())
            free_slots = GetAvailableSlotsQuery(self.repositories).execute(
                GetAvailableSlotsQueryDTO(service_id=service.id, day=start.date())
            )
            if start not in free_slots:
                raise SlotNotAvailable()
            appointment = self.repositories.appointments.create(
                client=client, service=service, start=start, source=dto.source, notes=dto.notes
            )
            if start - timezone.now() < REMINDER_WINDOW:
                appointment.reminder_sent_at = timezone.now()
                self.repositories.appointments.save(appointment, ["reminder_sent_at"])

        if dto.source in SOURCE_LABELS:
            text = customer_messages.owner_new_booking(SOURCE_LABELS[dto.source], client.name, service.name, start)
            NotifyOwnerCommand(self.repositories, self.message_service).execute(NotifyOwnerCommandDTO(text=text, client_id=client.id))
        return appointment
