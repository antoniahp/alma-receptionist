from django.conf import settings
from django.utils import timezone

from application.commands.send_message_to_client.command import SendMessageToClientCommand
from application.commands.send_message_to_client.command_dto import SendMessageToClientCommandDTO
from domain.entities import Notification
from domain.entities.chat_reply import ChatButton
from domain.rules import customer_messages


class SendReminderCommand:
    """Recordatorio con botones para confirmar o cambiar la cita."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        appointment = self.repositories.appointments.get(dto.appointment_id)
        appointment.ensure_active()
        buttons = [
            [ChatButton("✅ Allí estaré", f"confirm:{appointment.id}"), ChatButton("🔄 Cambiar la cita", f"change:{appointment.id}")]
        ]
        notification = SendMessageToClientCommand(self.repositories, self.message_service).execute(
            SendMessageToClientCommandDTO(
                client_id=appointment.client_id,
                kind=Notification.REMINDER,
                text=customer_messages.reminder_text(appointment, settings.BUSINESS["name"]),
                buttons=buttons,
                appointment_id=appointment.id,
                service_id=appointment.service_id,
            )
        )
        if notification.status != Notification.FAILED:
            appointment.reminder_sent_at = timezone.now()
            self.repositories.appointments.save(appointment, ["reminder_sent_at"])
        return notification
