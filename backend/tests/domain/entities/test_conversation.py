import pytest
from model_bakery import baker

from domain.entities import Conversation


def test_set_state_adds_and_removes_values():
    conversation = Conversation(key="web:abc")

    conversation.set_state(awaiting="name", service_id=3)
    conversation.set_state(awaiting=None)

    assert conversation.state == {"service_id": 3}


@pytest.mark.django_db
def test_channel_and_telegram_chat_id():
    telegram = baker.make(Conversation, key="tg:555")
    web = baker.make(Conversation, key="web:abc")

    assert telegram.channel == "telegram"
    assert telegram.telegram_chat_id == "555"
    assert web.channel == "web"
    assert web.telegram_chat_id is None
