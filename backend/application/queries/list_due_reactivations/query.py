from django.utils import timezone

from domain.entities.reactivation_candidate import ReactivationCandidate
from domain.rules.reactivation_rules import calculate_due_date, is_reactivation_due


class ListDueReactivationsQuery:
    """Clientas a las que les toca repetir un tratamiento y no tienen cita para él."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        today = dto.today or timezone.localdate()
        visits = self.repositories.appointments.last_completed_visits()
        already_booked = self.repositories.appointments.booked_client_service_pairs_since(timezone.now())
        services = {service.id: service for service in self.repositories.services.list(only_active=True)}
        clients = self.repositories.clients.get_many([visit["client_id"] for visit in visits])

        candidates = []
        for visit in visits:
            service = services.get(visit["service_id"])
            if service is None:
                continue
            if (visit["client_id"], visit["service_id"]) in already_booked:
                continue
            last_visit = timezone.localtime(visit["last_visit"])
            due = calculate_due_date(last_visit.date(), service.repeat_every_days)
            if not is_reactivation_due(due, today, dto.days_ahead):
                continue
            if self.repositories.notifications.reactivation_sent_since(visit["client_id"], service.id, visit["last_visit"]):
                continue
            candidates.append(
                ReactivationCandidate(
                    client=clients[visit["client_id"]],
                    service=service,
                    last_visit=last_visit,
                    days_since=(today - last_visit.date()).days,
                    due=due,
                    days_until_due=(due - today).days,
                )
            )
        candidates.sort(key=lambda candidate: candidate.days_until_due)
        return candidates
