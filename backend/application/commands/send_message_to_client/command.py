import logging

from domain.entities import Notification
from domain.exceptions import MessageNotSent

logger = logging.getLogger(__name__)


class SendMessageToClientCommand:
    """Envía un mensaje a una clienta por Telegram.

    Si Telegram no está configurado o la clienta aún no ha abierto el bot, se guarda como 'simulado'
    para que la dueña vea el texto en el panel.
    """

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        client = self.repositories.clients.get(dto.client_id)
        status = Notification.SIMULATED
        error = ""
        if not client.has_telegram:
            error = "La clienta aún no ha abierto el bot de Telegram"
        elif not self.message_service.is_enabled():
            error = "Telegram no está configurado"
        else:
            try:
                self.message_service.send(client.telegram_chat_id, dto.text, dto.buttons)
                status = Notification.SENT
            except MessageNotSent as exception:
                status = Notification.FAILED
                error = str(exception)[:300]
                logger.warning("No se pudo enviar a %s: %s", client, exception)
        return self.repositories.notifications.create(
            kind=dto.kind,
            text=dto.text,
            status=status,
            client_id=client.id,
            error=error,
            appointment_id=dto.appointment_id,
            service_id=dto.service_id,
        )
