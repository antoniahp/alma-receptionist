from django.db.models import Max

from domain.entities import Appointment
from domain.repositories.appointment_repository import AppointmentRepository


class DjangoAppointmentRepository(AppointmentRepository):
    def base_queryset(self):
        return Appointment.objects.select_related("client", "service")

    def get(self, appointment_id):
        return self.base_queryset().get(pk=appointment_id)

    def get_for_update(self, appointment_id):
        return self.base_queryset().select_for_update(of=("self",)).get(pk=appointment_id)

    def find_active_for_client(self, appointment_id, client_id):
        if not appointment_id or not client_id:
            return None
        return self.base_queryset().filter(pk=appointment_id, client_id=client_id, status__in=Appointment.ACTIVE_STATUSES).first()

    def create(self, client, service, start, source, notes=""):
        return Appointment.objects.create(client=client, service=service, start=start, source=source, notes=notes, price=service.price)

    def save(self, appointment, fields):
        appointment.save(update_fields=fields)

    def list_active_between(self, start, end, exclude_appointment_id=None):
        appointments = self.base_queryset().filter(status__in=Appointment.ACTIVE_STATUSES, start__gte=start, start__lt=end)
        if exclude_appointment_id:
            appointments = appointments.exclude(pk=exclude_appointment_id)
        return list(appointments)

    def list_active_since(self, since):
        appointments = (
            self.base_queryset()
            .filter(status__in=Appointment.ACTIVE_STATUSES, start__gte=since)
            .prefetch_related("service__consumption")
            .order_by("start")
        )
        return list(appointments)

    def list_without_reminder_between(self, start, end):
        appointments = self.base_queryset().filter(
            status__in=Appointment.ACTIVE_STATUSES, reminder_sent_at__isnull=True, start__gt=start, start__lte=end
        )
        return list(appointments.order_by("start"))

    def list_between(self, start=None, end=None, statuses=None):
        appointments = self.base_queryset().prefetch_related("service__consumption__product")
        if start:
            appointments = appointments.filter(start__gte=start)
        if end:
            appointments = appointments.filter(start__lt=end)
        if statuses:
            appointments = appointments.filter(status__in=statuses)
        return list(appointments.order_by("start"))

    def list_upcoming_for_client(self, client_id, since):
        appointments = self.base_queryset().filter(client_id=client_id, status__in=Appointment.ACTIVE_STATUSES, start__gte=since)
        return list(appointments.order_by("start"))

    def last_completed_for_client(self, client_id):
        return self.base_queryset().filter(client_id=client_id, status=Appointment.COMPLETED).order_by("-start").first()

    def last_completed_visits(self):
        rows = (
            Appointment.objects.filter(
                status=Appointment.COMPLETED,
                service__repeat_every_days__isnull=False,
                client__accepts_reminders=True,
            )
            .values("client_id", "service_id")
            .annotate(last_visit=Max("start"))
        )
        return list(rows)

    def booked_client_service_pairs_since(self, since):
        pairs = Appointment.objects.filter(status__in=Appointment.ACTIVE_STATUSES, start__gte=since).values_list("client_id", "service_id")
        return set(pairs)

    def list_for_client(self, client_id, limit=30):
        return list(self.base_queryset().filter(client_id=client_id).order_by("-start")[:limit])
