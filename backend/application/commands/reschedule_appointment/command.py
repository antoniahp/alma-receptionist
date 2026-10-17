from django.db import transaction
from django.utils import timezone

from application.commands.notify_owner.command import NotifyOwnerCommand
from application.commands.notify_owner.command_dto import NotifyOwnerCommandDTO
from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from domain.entities import Appointment
from domain.exceptions import SlotNotAvailable
from domain.rules import customer_messages


class RescheduleAppointmentCommand:
    """Cambia la cita de hora. Vuelve a estado 'reservada' y se enviará un nuevo recordatorio."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        new_start = timezone.localtime(dto.new_start)
        with transaction.atomic():
            self.repositories.opening_hours.lock_weekday(new_start.weekday())
            appointment = self.repositories.appointments.get(dto.appointment_id)
            appointment.ensure_active()
            free_slots = GetAvailableSlotsQuery(self.repositories).execute(
                GetAvailableSlotsQueryDTO(service_id=appointment.service_id, day=new_start.date(), exclude_appointment_id=appointment.id)
            )
            if new_start not in free_slots:
                raise SlotNotAvailable()
            old_start = appointment.start
            appointment.start = new_start
            appointment.status = Appointment.BOOKED
            appointment.reminder_sent_at = None
            self.repositories.appointments.save(appointment, ["start", "status", "reminder_sent_at"])

        if dto.notify_owner:
            text = customer_messages.owner_rescheduled(appointment.client.name, appointment.service.name, old_start, new_start)
            NotifyOwnerCommand(self.repositories, self.message_service).execute(
                NotifyOwnerCommandDTO(text=text, client_id=appointment.client_id)
            )
        return appointment
