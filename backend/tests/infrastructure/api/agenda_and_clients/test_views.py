from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from domain.entities import Appointment, Expense
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def test_block_list_and_delete(owner_client, salon, next_monday):
    created = owner_client.post(
        "/api/blocks/",
        {"start": local_datetime(next_monday, 10).isoformat(), "end": local_datetime(next_monday, 14).isoformat(), "reason": "Formación"},
        format="json",
    )
    day = next_monday.isoformat()
    listed = owner_client.get(f"/api/blocks/?start={day}&end={day}").json()
    free = owner_client.get(f"/api/public/availability/?service={salon.massage.id}&date={day}").json()["slots"]

    assert created.status_code == 201
    assert listed[0]["reason"] == "Formación"
    assert all(timezone.localtime(timezone.datetime.fromisoformat(slot)).hour >= 16 for slot in free)

    assert owner_client.delete(f"/api/blocks/{listed[0]['id']}/").status_code == 204
    assert owner_client.get(f"/api/blocks/?start={day}&end={day}").json() == []


def test_create_and_edit_a_treatment(owner_client):
    created = owner_client.post(
        "/api/services/",
        {"name": "Lifting de pestañas", "category": "cejas_pestanas", "price": "35", "duration_minutes": 60},
        format="json",
    ).json()

    edited = owner_client.patch(
        f"/api/services/{created['id']}/",
        {"name": "Lifting de pestañas", "category": "cejas_pestanas", "price": "38.50", "duration_minutes": 60, "active": True},
        format="json",
    )

    assert edited.json()["price"] == "38.50"


def test_client_file_and_forget(owner_client, salon):
    baker.make(
        Appointment,
        client=salon.laura,
        service=salon.massage,
        start=timezone.now() - timedelta(days=3),
        status=Appointment.COMPLETED,
        price=45,
    )

    client_file = owner_client.get(f"/api/clients/{salon.laura.id}/").json()
    forgotten = owner_client.post(f"/api/clients/{salon.laura.id}/forget/").json()

    assert client_file["visits"] == 1
    assert client_file["appointments"][0]["service_name"] == salon.massage.name
    assert forgotten["name"] == "Clienta borrada"


def test_export_month_as_csv(owner_client, salon):
    today = timezone.localdate()
    baker.make(
        Appointment,
        client=salon.laura,
        service=salon.massage,
        start=timezone.now(),
        status=Appointment.COMPLETED,
        price=45,
        payment_method="tarjeta",
    )
    baker.make(Expense, concept="Luz", category="suministros", amount="60.10", date=today)

    response = owner_client.get(f"/api/finances/export/?month={today:%Y-%m}")
    text = response.content.decode("utf-8")

    assert response["Content-Type"].startswith("text/csv")
    assert text.startswith("﻿Fecha;Tipo;Concepto")
    assert "Ingreso;" in text and ";Tarjeta;45,00" in text
    assert "Gasto;Luz;Luz, agua e internet;;60,10" in text


def test_public_booking_without_privacy_is_rejected(api_client, salon, next_monday):
    response = api_client.post(
        "/api/public/book/",
        {"service": str(salon.massage.id), "start": local_datetime(next_monday, 10).isoformat(), "name": "Irene", "phone": "699"},
        format="json",
    )

    assert response.status_code == 400
    assert "privacidad" in response.json()["detail"]


def test_public_info_has_legal_details(api_client, salon):
    info = api_client.get("/api/public/info/").json()

    assert info["nif"] == "00000000T"
    assert info["email"] == "hola@centro.example"
