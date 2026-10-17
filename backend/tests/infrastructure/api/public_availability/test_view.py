from datetime import timedelta

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


def test_returns_slots_without_login(api_client, salon, next_monday):
    response = api_client.get("/api/public/availability/", {"service": str(salon.massage.id), "date": next_monday.isoformat()})

    assert response.status_code == 200
    assert response.json()["slots"][0].startswith(f"{next_monday:%Y-%m-%d}T10:00:00")


def test_rejects_past_and_far_dates(api_client, salon):
    yesterday = timezone.localdate() - timedelta(days=1)
    far = timezone.localdate() + timedelta(days=60)

    assert api_client.get("/api/public/availability/", {"service": str(salon.massage.id), "date": yesterday.isoformat()}).status_code == 400
    assert api_client.get("/api/public/availability/", {"service": str(salon.massage.id), "date": far.isoformat()}).status_code == 400


def test_bad_service_id(api_client, salon, next_monday):
    assert api_client.get("/api/public/availability/", {"service": "123", "date": next_monday.isoformat()}).status_code == 400
