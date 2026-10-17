import re

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Max, Min, Q
from django.utils import timezone

from domain.entities import Appointment, Client, Conversation, Notification
from domain.entities.client import new_link_code
from domain.repositories.client_repository import ClientRepository


class DjangoClientRepository(ClientRepository):
    def get(self, client_id):
        return Client.objects.get(pk=client_id)

    def find(self, client_id):
        if not client_id:
            return None
        try:
            return Client.objects.filter(pk=client_id).first()
        except ValidationError:
            return None

    def find_by_phone(self, phone):
        """Compara solo las cifras (sin prefijo): '600123456' y '+34 600 12 34 56' son el mismo teléfono."""
        wanted = re.sub(r"\D", "", phone or "")[-9:]
        if len(wanted) < 9:
            return None
        for client in Client.objects.exclude(phone=""):
            if re.sub(r"\D", "", client.phone)[-9:] == wanted:
                return client
        return None

    def find_by_telegram_chat(self, chat_id):
        return Client.objects.filter(telegram_chat_id=chat_id).first()

    def find_by_link_code(self, link_code):
        if not link_code:
            return None
        return Client.objects.filter(telegram_link_code=link_code).first()

    def create(self, name, phone="", telegram_chat_id=None, email="", notes=""):
        return Client.objects.create(name=name, phone=phone, telegram_chat_id=telegram_chat_id, email=email, notes=notes)

    def save(self, client, fields):
        client.save(update_fields=fields)

    def search(self, text=""):
        completed = Q(appointments__status=Appointment.COMPLETED)
        upcoming = Q(appointments__status__in=Appointment.ACTIVE_STATUSES, appointments__start__gte=timezone.now())
        clients = Client.objects.annotate(
            visits_count=Count("appointments", filter=completed),
            last_visit=Max("appointments__start", filter=completed),
            next_visit=Min("appointments__start", filter=upcoming),
        )
        if text:
            clients = clients.filter(Q(name__icontains=text) | Q(phone__icontains=text) | Q(email__icontains=text))
        return list(clients.order_by("name"))

    def get_many(self, client_ids):
        return Client.objects.in_bulk(list(client_ids))

    def list_review_candidates(self, completed_before, min_visits):
        completed = Q(appointments__status=Appointment.COMPLETED)
        clients = Client.objects.filter(telegram_chat_id__isnull=False, review_requested_at__isnull=True).annotate(
            visits_count=Count("appointments", filter=completed),
            last_visit=Max("appointments__start", filter=completed),
        )
        return list(clients.filter(visits_count__gte=min_visits, last_visit__lt=completed_before))

    def forget(self, client):
        with transaction.atomic():
            Conversation.objects.filter(client=client).delete()
            Notification.objects.filter(client=client).delete()
            client.appointments.update(notes="")
            client.name = "Clienta borrada"
            client.phone = ""
            client.email = ""
            client.notes = ""
            client.telegram_chat_id = None
            client.telegram_link_code = new_link_code()
            client.accepts_reminders = False
            client.privacy_accepted_at = None
            client.save()
