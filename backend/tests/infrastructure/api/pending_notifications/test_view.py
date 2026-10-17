from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from domain.entities import Appointment

pytestmark = pytest.mark.django_db


def test_lists_reminders_and_reactivations(owner_client, salon):
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timedelta(hours=20))
    marta = baker.make("domain.Client", name="Marta Ruiz")
    baker.make(Appointment, client=marta, service=salon.massage, status=Appointment.COMPLETED, start=timezone.now() - timedelta(days=31))

    data = owner_client.get("/api/notifications/pending/").json()

    assert data["reminders"][0]["appointment"]["client_name"] == "Laura Gómez"
    assert data["reactivations"][0]["client"]["name"] == "Marta Ruiz"
    assert data["reactivations"][0]["service"]["name"] == "Masaje relajante"
