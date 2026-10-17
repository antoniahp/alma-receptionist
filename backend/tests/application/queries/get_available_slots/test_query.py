from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from domain.entities import Appointment
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def hours(slots):
    return [f"{timezone.localtime(slot):%H:%M}" for slot in slots]


def test_returns_slots_inside_opening_hours(repositories, salon, next_monday):
    slots = GetAvailableSlotsQuery(repositories).execute(GetAvailableSlotsQueryDTO(service_id=salon.massage.id, day=next_monday))

    assert hours(slots)[0] == "10:00"
    assert "13:00" in hours(slots)
    assert "13:30" not in hours(slots)
    assert "16:00" in hours(slots)


def test_booked_time_is_not_available(repositories, salon, next_monday):
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=local_datetime(next_monday, 10))

    slots = GetAvailableSlotsQuery(repositories).execute(GetAvailableSlotsQueryDTO(service_id=salon.massage.id, day=next_monday))

    assert "10:00" not in hours(slots)
    assert "10:30" not in hours(slots)
    assert "11:00" in hours(slots)


def test_cancelled_appointments_free_the_slot(repositories, salon, next_monday):
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=local_datetime(next_monday, 10), status=Appointment.CANCELLED)

    slots = GetAvailableSlotsQuery(repositories).execute(GetAvailableSlotsQueryDTO(service_id=salon.massage.id, day=next_monday))

    assert "10:00" in hours(slots)


def test_closed_on_sunday(repositories, salon, next_monday):
    sunday = next_monday - timedelta(days=1)

    assert GetAvailableSlotsQuery(repositories).execute(GetAvailableSlotsQueryDTO(service_id=salon.massage.id, day=sunday)) == []
