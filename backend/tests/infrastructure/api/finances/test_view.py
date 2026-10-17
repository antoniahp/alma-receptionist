import pytest

pytestmark = pytest.mark.django_db


def test_owner_adds_an_expense_and_sees_it_in_the_month(owner_client, salon):
    created = owner_client.post(
        "/api/expenses/", {"concept": "Alquiler", "category": "alquiler", "amount": "650.00", "date": "2026-03-01"}, format="json"
    )
    assert created.status_code == 201

    finances = owner_client.get("/api/finances/", {"month": "2026-03"}).json()

    assert finances["other_spending"] == "650.00"
    assert finances["expenses"][0]["category_label"] == "Alquiler"
    assert len(finances["history"]) == 6


def test_owner_deletes_an_expense(owner_client, salon):
    expense_id = owner_client.post("/api/expenses/", {"concept": "Luz", "amount": "80", "date": "2026-03-10"}, format="json").json()["id"]

    assert owner_client.delete(f"/api/expenses/{expense_id}/").status_code == 204
    assert owner_client.get("/api/finances/", {"month": "2026-03"}).json()["expenses"] == []


def test_amount_must_be_positive(owner_client, salon):
    response = owner_client.post("/api/expenses/", {"concept": "Luz", "amount": "0", "date": "2026-03-10"}, format="json")

    assert response.status_code == 400


def test_bad_month_is_rejected(owner_client, salon):
    assert owner_client.get("/api/finances/", {"month": "marzo"}).status_code == 400


def test_clients_cannot_see_the_finances(api_client, salon):
    assert api_client.get("/api/finances/").status_code == 401
