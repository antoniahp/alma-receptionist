import pytest
from django.core import mail
from model_bakery import baker

from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def test_full_order_flow(owner_client, salon, next_monday, fake_services):
    for hour in (10, 11, 12):
        owner_client.post(
            "/api/appointments/",
            {"client": str(salon.laura.id), "service": str(salon.massage.id), "start": local_datetime(next_monday, hour).isoformat()},
            format="json",
        )

    drafts = owner_client.post("/api/orders/generate/").json()
    order_id = drafts[0]["id"]
    assert drafts[0]["lines"][0]["units"] == 2

    edited = owner_client.patch(f"/api/orders/{order_id}/", {"email_subject": "Pedido urgente", "email_body": "Hola Pilar"}, format="json")
    assert edited.json()["email_subject"] == "Pedido urgente"

    approved = owner_client.post(f"/api/orders/{order_id}/approve/")
    assert approved.json()["status"] == "sent"
    assert fake_services["email_service"].sent[0]["subject"] == "Pedido urgente"

    received = owner_client.post(f"/api/orders/{order_id}/receive/")
    assert received.json()["status"] == "received"
    salon.oil.refresh_from_db()
    assert salon.oil.stock_uses == 14
    assert mail.outbox == []  # el correo real nunca se usa en los tests


def test_sent_order_cannot_be_edited(owner_client, salon):
    order = baker.make("domain.PurchaseOrder", supplier=salon.supplier, status="sent")

    response = owner_client.patch(f"/api/orders/{order.id}/", {"email_subject": "x", "email_body": "y"}, format="json")

    assert response.status_code == 400
