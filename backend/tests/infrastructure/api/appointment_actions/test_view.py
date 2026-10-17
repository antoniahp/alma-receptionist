import uuid

import pytest
from model_bakery import baker

from domain.entities import Appointment

pytestmark = pytest.mark.django_db


def test_complete_returns_used_products(owner_client, salon):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage)

    response = owner_client.post(f"/api/appointments/{appointment.id}/complete/")

    assert response.status_code == 200
    assert response.json()["appointment"]["status"] == "completed"
    assert response.json()["used"] == [{"product": "Aceite de almendras", "uses": 1}]


def test_completing_twice_is_rejected(owner_client, salon):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage)
    owner_client.post(f"/api/appointments/{appointment.id}/complete/")

    response = owner_client.post(f"/api/appointments/{appointment.id}/complete/")

    assert response.status_code == 400


def test_unknown_appointment_is_404(owner_client, salon):
    assert owner_client.post(f"/api/appointments/{uuid.uuid4()}/cancel/").status_code == 404


def test_remind_returns_notification(owner_client, salon):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage)

    response = owner_client.post(f"/api/appointments/{appointment.id}/remind/")

    assert response.json()["status"] == "simulated"
