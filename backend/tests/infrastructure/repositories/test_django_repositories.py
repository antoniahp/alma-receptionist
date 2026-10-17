import pytest
from model_bakery import baker

from domain.entities import ChatMessage, Conversation

pytestmark = pytest.mark.django_db


def test_find_returns_none_for_invalid_ids(repositories, salon):
    assert repositories.clients.find("no-es-un-uuid") is None
    assert repositories.services.find_active("no-es-un-uuid") is None
    assert repositories.services.find_active(None) is None


def test_find_active_service_ignores_inactive(repositories, salon):
    salon.massage.active = False
    salon.massage.save()

    assert repositories.services.find_active(salon.massage.id) is None


def test_change_stock_records_movement(repositories, salon):
    repositories.products.change_stock(salon.oil, -2, "cita")

    salon.oil.refresh_from_db()
    assert salon.oil.stock_uses == 2
    assert salon.oil.movements.get().change == -2


def test_owner_messages_after_a_given_message(repositories):
    conversation = baker.make(Conversation, key="web:abc")
    first = repositories.conversations.add_message(conversation, ChatMessage.USER, "hola")
    reply = repositories.conversations.add_message(conversation, ChatMessage.ASSISTANT, "¡Sí!", from_owner=True)

    assert repositories.conversations.owner_messages_after("web:abc", first.id) == [reply]
    assert repositories.conversations.owner_messages_after("web:abc", reply.id) == []
    assert repositories.conversations.owner_messages_after("web:abc", "basura") == [reply]


def test_recent_conversations_skip_the_ones_where_nobody_wrote(repositories):
    empty = baker.make(Conversation, key="web:vacia")
    baker.make(ChatMessage, conversation=empty, role=ChatMessage.ASSISTANT, text="¡Hola!")
    real = baker.make(Conversation, key="web:real")
    baker.make(ChatMessage, conversation=real, role=ChatMessage.USER, text="¿Qué precio tiene el masaje?")

    assert repositories.conversations.list_recent(10) == [real]
