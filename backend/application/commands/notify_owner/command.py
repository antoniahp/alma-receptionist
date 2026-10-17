import logging

from django.conf import settings

from domain.entities import Notification
from domain.exceptions import MessageNotSent

logger = logging.getLogger(__name__)


class NotifyOwnerCommand:
    """Avisa a la dueña por Telegram (si tiene configurado su chat) y lo deja registrado."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        status = Notification.SIMULATED
        message_id = ""
        owner_chat_id = settings.TELEGRAM_OWNER_CHAT_ID
        if owner_chat_id and self.message_service.is_enabled():
            try:
                message_id = self.message_service.send(owner_chat_id, dto.text)
                status = Notification.SENT
            except MessageNotSent as error:
                logger.warning("No se pudo avisar a la dueña: %s", error)
                status = Notification.FAILED
        return self.repositories.notifications.create(
            kind=Notification.OWNER,
            text=dto.text,
            status=status,
            client_id=dto.client_id,
            telegram_message_id=str(message_id or ""),
        )
