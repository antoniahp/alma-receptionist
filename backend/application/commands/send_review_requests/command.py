from django.conf import settings
from django.utils import timezone

from application.commands.send_message_to_client.command import SendMessageToClientCommand
from application.commands.send_message_to_client.command_dto import SendMessageToClientCommandDTO
from application.shared.schedule import start_of_day
from domain.entities import Notification
from domain.rules import customer_messages


class SendReviewRequestsCommand:
    """Pide una reseña en Google una sola vez, al día siguiente de la tercera cita completada.

    Solo a clientas con Telegram y que aceptan mensajes. Sin GOOGLE_REVIEW_URL no hace nada.
    """

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        review_url = settings.GOOGLE_REVIEW_URL
        if not review_url:
            return 0
        now = timezone.localtime(dto.now or timezone.now())
        candidates = self.repositories.clients.list_review_candidates(
            completed_before=start_of_day(now.date()), min_visits=settings.REVIEW_AFTER_VISITS
        )
        sent = 0
        for client in candidates:
            if not client.accepts_reminders:
                continue
            SendMessageToClientCommand(self.repositories, self.message_service).execute(
                SendMessageToClientCommandDTO(
                    client_id=client.id,
                    kind=Notification.REVIEW,
                    text=customer_messages.review_request(client.first_name, settings.BUSINESS["name"], review_url),
                )
            )
            # Se marca aunque falle el envío: mejor no pedirla que pedirla dos veces
            client.review_requested_at = now
            self.repositories.clients.save(client, ["review_requested_at"])
            sent += 1
        return sent
