from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.queries.get_dashboard.query import GetDashboardQuery
from application.queries.get_dashboard.query_dto import GetDashboardQueryDTO
from domain.entities import Appointment, HelpRequest

pytestmark = pytest.mark.django_db


def test_counts_open_help_requests(repositories, salon):
    baker.make(HelpRequest, status=HelpRequest.OPEN)
    baker.make(HelpRequest, status=HelpRequest.CLOSED)

    dashboard = GetDashboardQuery(repositories).execute(GetDashboardQueryDTO())

    assert dashboard["help_requests_open"] == 1
    assert set(dashboard) == {
        "appointments_today",
        "revenue_today",
        "reminders_due",
        "reactivations_due",
        "products_to_order",
        "orders_to_approve",
        "help_requests_open",
        "latest_help_request",
    }


def test_pending_reminders_only_count_clients_who_can_receive_them(repositories, salon):
    soon = timezone.now() + timedelta(hours=5)
    with_telegram = baker.make("domain.Client", name="Con Telegram", telegram_chat_id="123")
    baker.make(Appointment, client=with_telegram, service=salon.massage, start=soon)
    baker.make(Appointment, client=salon.laura, service=salon.massage, start=soon + timedelta(hours=1))

    dashboard = GetDashboardQuery(repositories).execute(GetDashboardQueryDTO())

    assert dashboard["reminders_due"] == 1
