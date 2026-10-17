from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.queries.list_due_reactivations.query import ListDueReactivationsQuery
from application.queries.list_due_reactivations.query_dto import ListDueReactivationsQueryDTO
from domain.entities import Appointment, Notification

pytestmark = pytest.mark.django_db


def last_visit(salon, days_ago):
    return baker.make(
        Appointment,
        client=salon.laura,
        service=salon.massage,
        status=Appointment.COMPLETED,
        start=timezone.now() - timedelta(days=days_ago),
    )


def test_due_when_repeat_period_has_passed(repositories, salon):
    last_visit(salon, days_ago=31)

    candidates = ListDueReactivationsQuery(repositories).execute(ListDueReactivationsQueryDTO())

    assert len(candidates) == 1
    assert candidates[0].client == salon.laura
    assert candidates[0].days_since == 31


def test_not_due_too_early(repositories, salon):
    last_visit(salon, days_ago=10)

    assert ListDueReactivationsQuery(repositories).execute(ListDueReactivationsQueryDTO()) == []


def test_not_due_if_already_booked(repositories, salon):
    last_visit(salon, days_ago=31)
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=timezone.now() + timedelta(days=3))

    assert ListDueReactivationsQuery(repositories).execute(ListDueReactivationsQueryDTO()) == []


def test_not_due_if_already_contacted(repositories, salon):
    last_visit(salon, days_ago=31)
    baker.make(Notification, client=salon.laura, service=salon.massage, kind=Notification.REACTIVATION, status=Notification.SENT)

    assert ListDueReactivationsQuery(repositories).execute(ListDueReactivationsQueryDTO()) == []


def test_not_due_if_client_does_not_want_messages(repositories, salon):
    salon.laura.accepts_reminders = False
    salon.laura.save()
    last_visit(salon, days_ago=31)

    assert ListDueReactivationsQuery(repositories).execute(ListDueReactivationsQueryDTO()) == []
