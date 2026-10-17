import pytest
from model_bakery import baker

from domain.entities import Conversation, HelpRequest

pytestmark = pytest.mark.django_db


def test_dashboard_numbers(owner_client, salon):
    data = owner_client.get("/api/dashboard/").json()

    assert data["appointments_today"] == 0
    assert data["help_requests_open"] == 0
    assert data["revenue_today"] == "0.00"
    assert data["latest_help_request"] is None


def test_dashboard_has_the_last_question_aura_could_not_answer(owner_client, salon):
    conversation = baker.make(Conversation, key="web:1", client=salon.laura)
    baker.make(HelpRequest, conversation=conversation, client=salon.laura, question="¿Hacéis hilo?", status=HelpRequest.OPEN)

    data = owner_client.get("/api/dashboard/").json()

    assert data["latest_help_request"]["question"] == "¿Hacéis hilo?"
    assert data["latest_help_request"]["client_name"] == salon.laura.name
