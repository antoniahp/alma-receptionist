import pytest

from application.commands.start_chat.command import StartChatCommand
from application.commands.start_chat.command_dto import StartChatCommandDTO
from tests.helpers import button_data

pytestmark = pytest.mark.django_db


def test_greets_by_name_with_menu(repositories, salon, message_service):
    reply = StartChatCommand(repositories, message_service).execute(
        StartChatCommandDTO(conversation_key="tg:555", client_id=salon.laura.id)
    )

    assert reply.text.startswith("¡Hola, Laura! Soy Aura")
    assert button_data(reply) == ["book", "prices", "hours"]


def test_telegram_greeting_links_the_privacy_policy(repositories, message_service):
    reply = StartChatCommand(repositories, message_service).execute(StartChatCommandDTO(conversation_key="tg:123"))

    assert "https://centro.example/privacidad" in reply.text


def test_web_greeting_does_not_repeat_the_privacy_link(repositories, message_service):
    reply = StartChatCommand(repositories, message_service).execute(StartChatCommandDTO(conversation_key="web:abc"))

    assert "privacidad" not in reply.text
