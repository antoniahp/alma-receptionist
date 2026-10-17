import pytest
from model_bakery import baker

from application.commands.link_telegram_chat.command import LinkTelegramChatCommand
from application.commands.link_telegram_chat.command_dto import LinkTelegramChatCommandDTO
from domain.entities import Client

pytestmark = pytest.mark.django_db


def test_links_chat_with_booking_code(repositories, salon):
    client = LinkTelegramChatCommand(repositories).execute(
        LinkTelegramChatCommandDTO(chat_id="555", link_code=salon.laura.telegram_link_code)
    )

    assert client == salon.laura
    salon.laura.refresh_from_db()
    assert salon.laura.telegram_chat_id == "555"


def test_creates_client_for_unknown_chat(repositories, db):
    client = LinkTelegramChatCommand(repositories).execute(LinkTelegramChatCommandDTO(chat_id="777", first_name="Rocío", last_name="Sanz"))

    assert client.name == "Rocío Sanz"
    assert Client.objects.count() == 1


def test_moves_chat_to_the_right_client(repositories, salon):
    wrong = baker.make(Client, name="Laura", telegram_chat_id="555")

    LinkTelegramChatCommand(repositories).execute(LinkTelegramChatCommandDTO(chat_id="555", link_code=salon.laura.telegram_link_code))

    wrong.refresh_from_db()
    salon.laura.refresh_from_db()
    assert wrong.telegram_chat_id is None
    assert salon.laura.telegram_chat_id == "555"
