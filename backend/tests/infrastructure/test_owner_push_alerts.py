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


def ask(key, text):
    from application.commands.handle_chat_message.command import HandleChatMessageCommand
    from application.commands.handle_chat_message.command_dto import HandleChatMessageCommandDTO
    from infrastructure.repositories.django_repositories import build_django_repositories
    from tests.fakes import FakeLanguageModelService, FakeMessageService

    HandleChatMessageCommand(build_django_repositories(), FakeMessageService(), FakeLanguageModelService()).execute(
        HandleChatMessageCommandDTO(conversation_key=key, text=text)
    )


def test_one_alert_per_client_however_many_times_she_writes(alerts, salon):
    for text in ["Soy alérgica al látex, ¿puedo hacerme pestañas?", "¿Y con otro pegamento?", "Es que tengo boda el sábado"]:
        ask("web:misma-clienta", text)

    assert len(alerts) == 1


def test_five_clients_writing_means_five_alerts(alerts, salon):
    for number in range(5):
        ask(f"web:clienta-{number}", "Estoy embarazada, ¿puedo hacerme un peeling?")

    assert len(alerts) == 5
