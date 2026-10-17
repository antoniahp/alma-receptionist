from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.queries.list_due_reminders.query import ListDueRemindersQuery
from application.queries.list_due_reminders.query_dto import ListDueRemindersQueryDTO
from domain.entities import Appointment

pytestmark = pytest.mark.django_db


def test_only_active_appointments_in_the_next_24_hours(repositories, salon):
    now = timezone.now()
    due = baker.make(Appointment, client=salon.laura, service=salon.massage, start=now + timedelta(hours=20))
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=now + timedelta(hours=30))
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=now + timedelta(hours=5), status=Appointment.CANCELLED)
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=now + timedelta(hours=6), reminder_sent_at=now)

    assert ListDueRemindersQuery(repositories).execute(ListDueRemindersQueryDTO()) == [due]
