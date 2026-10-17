from django.utils import timezone

from application.commands.send_reactivation.command import SendReactivationCommand
from application.commands.send_reactivation.command_dto import SendReactivationCommandDTO
from application.commands.send_reminder.command import SendReminderCommand
from application.commands.send_reminder.command_dto import SendReminderCommandDTO
from application.commands.send_review_requests.command import SendReviewRequestsCommand
from application.commands.send_review_requests.command_dto import SendReviewRequestsCommandDTO
from application.queries.list_due_reactivations.query import ListDueReactivationsQuery
from application.queries.list_due_reactivations.query_dto import ListDueReactivationsQueryDTO
from application.queries.list_due_reminders.query import ListDueRemindersQuery
from application.queries.list_due_reminders.query_dto import ListDueRemindersQueryDTO

FIRST_HOUR_FOR_REACTIVATIONS = 10
LAST_HOUR_FOR_REACTIVATIONS = 20


class SendDueNotificationsCommand:
    """Envía los recordatorios de las próximas 24 h y, en horario razonable, los mensajes para repetir y las peticiones de reseña.

    Solo a clientas con Telegram vinculado. Las demás se quedan pendientes: si abren el bot más tarde,
    les llegará en la siguiente vuelta.
    """

    def __init__(self, repositories, message_service, language_model_service):
        self.repositories = repositories
        self.message_service = message_service
        self.language_model_service = language_model_service

    def execute(self, dto):
        now = timezone.localtime(dto.now or timezone.now())
        sent = {"reminders": 0, "reactivations": 0, "reviews": 0}

        for appointment in ListDueRemindersQuery(self.repositories).execute(ListDueRemindersQueryDTO(now=now)):
            if not appointment.client.has_telegram:
                continue
            SendReminderCommand(self.repositories, self.message_service).execute(SendReminderCommandDTO(appointment_id=appointment.id))
            sent["reminders"] += 1

        if FIRST_HOUR_FOR_REACTIVATIONS <= now.hour < LAST_HOUR_FOR_REACTIVATIONS:
            candidates = ListDueReactivationsQuery(self.repositories).execute(ListDueReactivationsQueryDTO(today=now.date(), days_ahead=0))
            for candidate in candidates:
                if not candidate.client.has_telegram:
                    continue
                SendReactivationCommand(self.repositories, self.message_service, self.language_model_service).execute(
                    SendReactivationCommandDTO(client_id=candidate.client.id, service_id=candidate.service.id)
                )
                sent["reactivations"] += 1
            sent["reviews"] = SendReviewRequestsCommand(self.repositories, self.message_service).execute(
                SendReviewRequestsCommandDTO(now=now)
            )
        return sent
