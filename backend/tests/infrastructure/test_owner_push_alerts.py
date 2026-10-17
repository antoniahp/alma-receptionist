import pytest
from model_bakery import baker

from domain.entities import ChatMessage, Conversation, HelpRequest, Notification
from infrastructure import owner_push_alerts

pytestmark = pytest.mark.django_db


@pytest.fixture
def alerts(monkeypatch):
    sent = []
    monkeypatch.setattr(owner_push_alerts, "send_in_background", lambda title, body, url: sent.append((title, body, url)))
    return sent


def test_the_owner_is_alerted_when_aura_passes_her_a_question(alerts, salon):
    conversation = baker.make(Conversation, key="web:1", client=salon.laura)

    baker.make(HelpRequest, conversation=conversation, client=salon.laura, question="¿Hacéis depilación con hilo?")

    assert alerts == [(f"🙋 {salon.laura.name} tiene una pregunta", "¿Hacéis depilación con hilo?", "/panel/mensajes")]


def test_messages_and_bookings_do_not_alert_her(alerts, salon):
    conversation = baker.make(Conversation, key="web:2")
    ChatMessage.objects.create(conversation=conversation, role=ChatMessage.USER, text="Hola")
    baker.make(Notification, kind=Notification.OWNER, text="📅 Nueva cita por la web")

    assert alerts == []
