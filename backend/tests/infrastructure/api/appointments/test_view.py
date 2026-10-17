import pytest

from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def test_create_and_list_appointments(owner_client, salon, next_monday):
    start = local_datetime(next_monday, 10).isoformat()

    created = owner_client.post(
        "/api/appointments/", {"client": str(salon.laura.id), "service": str(salon.massage.id), "start": start}, format="json"
    )
    listed = owner_client.get("/api/appointments/", {"from": next_monday.isoformat(), "to": next_monday.isoformat()})

    assert created.status_code == 201
    item = listed.json()[0]
    assert item["id"] == created.json()["id"]
    assert item["client_name"] == "Laura Gómez"
    assert item["source"] == "owner"
    assert item["consumption"] == [{"product": "Aceite de almendras", "uses": 1}]
    assert item["start"].startswith(f"{next_monday:%Y-%m-%d}T10:00:00")


def test_double_booking_returns_conflict(owner_client, salon, next_monday):
    data = {"client": str(salon.laura.id), "service": str(salon.massage.id), "start": local_datetime(next_monday, 10).isoformat()}
    owner_client.post("/api/appointments/", data, format="json")

    response = owner_client.post("/api/appointments/", data, format="json")

    assert response.status_code == 409
    assert "no está libre" in response.json()["detail"]


def test_invalid_filters_return_400(owner_client):
    assert owner_client.get("/api/appointments/", {"from": "ayer"}).status_code == 400
