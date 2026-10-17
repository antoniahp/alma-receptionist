import pytest

pytestmark = pytest.mark.django_db


def test_book_and_conflict(api_client, salon, next_monday):
    slot = api_client.get("/api/public/availability/", {"service": str(salon.massage.id), "date": next_monday.isoformat()}).json()["slots"][
        0
    ]

    booked = api_client.post(
        "/api/public/book/",
        {"service": str(salon.massage.id), "start": slot, "name": "Irene Castro", "phone": "699", "privacy_accepted": True},
        format="json",
    )
    again = api_client.post(
        "/api/public/book/",
        {"service": str(salon.massage.id), "start": slot, "name": "Otra", "phone": "700", "privacy_accepted": True},
        format="json",
    )

    assert booked.status_code == 201
    assert booked.json()["client_name"] == "Irene"
    assert booked.json()["telegram_link"].startswith("https://t.me/alma_bot?start=")
    assert again.status_code == 409
    assert again.json()["detail"]


def test_name_is_required(api_client, salon, next_monday):
    response = api_client.post(
        "/api/public/book/", {"service": str(salon.massage.id), "start": "2030-01-07T10:00:00+01:00", "name": ""}, format="json"
    )

    assert response.status_code == 400
