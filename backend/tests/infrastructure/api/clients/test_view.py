import pytest
from model_bakery import baker

from domain.entities import Appointment

pytestmark = pytest.mark.django_db


def test_clients_list_shows_their_visits(owner_client, salon):
    baker.make(Appointment, client=salon.laura, service=salon.massage, status=Appointment.COMPLETED, start="2026-01-10T10:00:00+01:00")

    clients = owner_client.get("/api/clients/").json()

    assert clients[0]["name"] == "Laura Gómez"
    assert clients[0]["visits_count"] == 1
    assert clients[0]["last_visit"].startswith("2026-01-10")


def test_add_and_edit_a_client(owner_client, salon):
    created = owner_client.post("/api/clients/", {"name": "Rocío", "phone": "622334455"}, format="json")
    assert created.status_code == 201

    edited = owner_client.patch(
        f"/api/clients/{created.json()['id']}/", {"name": "Rocío Martín", "phone": "622334455", "notes": "Prefiere tardes"}, format="json"
    )
    assert edited.json()["notes"] == "Prefiere tardes"


def test_duplicated_phone_is_a_clear_error(owner_client, salon):
    response = owner_client.post("/api/clients/", {"name": "Otra", "phone": "611111111"}, format="json")

    assert response.status_code == 409
    assert "Laura" in response.json()["detail"]
