import pytest
from django.utils import timezone
from model_bakery import baker

from domain.entities import Appointment

pytestmark = pytest.mark.django_db


def test_complete_with_card_undo_and_cash_day(owner_client, salon):
    start = timezone.localtime().replace(hour=10, minute=0, second=0, microsecond=0)
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, start=start, price=45)

    completed = owner_client.post(f"/api/appointments/{appointment.id}/complete/", {"payment_method": "tarjeta"}, format="json")
    assert completed.json()["appointment"]["payment_method"] == "tarjeta"
    assert owner_client.get("/api/cash/").json()["card"] == "45.00"

    undone = owner_client.post(f"/api/appointments/{appointment.id}/undo-complete/")
    assert undone.json()["status"] == "booked"


def test_sell_a_pack_and_see_it_in_the_agenda(owner_client, salon):
    sold = owner_client.post(
        "/api/packs/",
        {"client": str(salon.laura.id), "service": str(salon.massage.id), "sessions": 5, "price": "200", "payment_method": "efectivo"},
        format="json",
    )
    assert sold.status_code == 201
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timezone.timedelta(days=1))

    appointments = owner_client.get("/api/appointments/").json()

    assert appointments[0]["client_has_pack"] is True


def test_close_cash(owner_client, salon):
    day = timezone.localdate().isoformat()

    closed = owner_client.post("/api/cash/", {"day": day, "counted_cash": "0"}, format="json")
    again = owner_client.post("/api/cash/", {"day": day, "counted_cash": "0"}, format="json")

    assert closed.json()["closing"]["difference"] == "0.00"
    assert again.status_code == 409
