import pytest
from django.utils import timezone

from application.queries.get_next_available_slots.query import GetNextAvailableSlotsQuery
from application.queries.get_next_available_slots.query_dto import GetNextAvailableSlotsQueryDTO

pytestmark = pytest.mark.django_db


def test_one_slot_per_day_by_default(repositories, salon, next_monday):
    slots = GetNextAvailableSlotsQuery(repositories).execute(
        GetNextAvailableSlotsQueryDTO(service_id=salon.massage.id, count=3, from_day=next_monday)
    )

    days = {timezone.localtime(slot).date() for slot in slots}
    assert len(slots) == 3
    assert len(days) == 3


def test_several_slots_the_same_day(repositories, salon, next_monday):
    slots = GetNextAvailableSlotsQuery(repositories).execute(
        GetNextAvailableSlotsQueryDTO(service_id=salon.massage.id, count=3, from_day=next_monday, one_per_day=False)
    )

    assert {timezone.localtime(slot).date() for slot in slots} == {next_monday}
