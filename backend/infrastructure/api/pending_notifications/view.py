from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_next_available_slots.query import GetNextAvailableSlotsQuery
from application.queries.get_next_available_slots.query_dto import GetNextAvailableSlotsQueryDTO
from application.queries.list_due_reactivations.query import ListDueReactivationsQuery
from application.queries.list_due_reactivations.query_dto import ListDueReactivationsQueryDTO
from application.queries.list_due_reminders.query import ListDueRemindersQuery
from application.queries.list_due_reminders.query_dto import ListDueRemindersQueryDTO
from domain.rules import customer_messages
from domain.rules import spanish_format as fmt
from infrastructure import dependencies
from infrastructure.api.pending_notifications.serializer import PendingNotificationsSerializer


class PendingNotificationsView(APIView):
    """Vista previa de los recordatorios y mensajes para repetir que se van a enviar."""

    def get(self, request):
        reminders = []
        for appointment in ListDueRemindersQuery(dependencies.get_repositories()).execute(ListDueRemindersQueryDTO()):
            reminders.append({"appointment": appointment, "text": customer_messages.reminder_text(appointment, settings.BUSINESS["name"])})

        reactivations = []
        for candidate in ListDueReactivationsQuery(dependencies.get_repositories()).execute(ListDueReactivationsQueryDTO()):
            slots = GetNextAvailableSlotsQuery(dependencies.get_repositories()).execute(
                GetNextAvailableSlotsQueryDTO(service_id=candidate.service.id, count=2)
            )
            reactivations.append(
                {
                    "client": candidate.client,
                    "service": candidate.service,
                    "days_since": candidate.days_since,
                    "days_until_due": candidate.days_until_due,
                    "preview": customer_messages.reactivation_text(candidate, slots),
                    "slots": [fmt.when(slot) for slot in slots],
                }
            )
        return Response(PendingNotificationsSerializer({"reminders": reminders, "reactivations": reactivations}).data)
