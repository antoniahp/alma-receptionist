from application.commands.notify_owner.command import NotifyOwnerCommand
from application.commands.notify_owner.command_dto import NotifyOwnerCommandDTO
from domain.entities import Appointment
from domain.rules import customer_messages


class CancelAppointmentCommand:
    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        appointment = self.repositories.appointments.get(dto.appointment_id)
        appointment.ensure_active()
        appointment.status = Appointment.CANCELLED
        self.repositories.appointments.save(appointment, ["status"])
        if dto.notify_owner:
            text = customer_messages.owner_cancelled(appointment.client.name, appointment.service.name, appointment.start)
            NotifyOwnerCommand(self.repositories, self.message_service).execute(
                NotifyOwnerCommandDTO(text=text, client_id=appointment.client_id)
            )
        return appointment
