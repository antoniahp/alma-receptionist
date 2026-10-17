from datetime import timedelta

from django.utils import timezone


class ListDueRemindersQuery:
    """Citas de las próximas 24 horas que aún no tienen recordatorio."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        now = dto.now or timezone.now()
        return self.repositories.appointments.list_without_reminder_between(now, now + timedelta(hours=24))
