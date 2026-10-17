import pytest
from model_bakery import baker

from application.commands.answer_help_request.command import AnswerHelpRequestCommand
from application.commands.answer_help_request.command_dto import AnswerHelpRequestCommandDTO
from domain.entities import ChatMessage, Conversation, HelpRequest
from domain.exceptions import EmptyAnswer, MessageNotSent
from tests.fakes import FakeMessageService

pytestmark = pytest.mark.django_db


def help_request_for(key, client=None):
    conversation = baker.make(Conversation, key=key, client=client)
    return baker.make(HelpRequest, conversation=conversation, client=client, question="¿Láser?")


def test_telegram_answer_goes_to_client_as_the_receptionist(repositories, salon, message_service):
    help_request = help_request_for("tg:555", salon.laura)

    AnswerHelpRequestCommand(repositories, message_service).execute(
        AnswerHelpRequestCommandDTO(help_request_id=help_request.id, text="¡Sí, desde noviembre!")
    )

    help_request.refresh_from_db()
    assert message_service.sent == [{"chat_id": "555", "text": "¡Sí, desde noviembre!", "buttons": []}]
    assert help_request.status == HelpRequest.ANSWERED


def test_web_answer_is_saved_for_the_chat_to_pick_up(repositories, salon, message_service):
    help_request = help_request_for("web:abc")

    AnswerHelpRequestCommand(repositories, message_service).execute(
        AnswerHelpRequestCommandDTO(help_request_id=help_request.id, text="¡Sí!")
    )

    message = ChatMessage.objects.get()
    assert message.from_owner is True
    assert message_service.sent == []


def test_signed_answer(repositories, salon, message_service):
    help_request = help_request_for("tg:555", salon.laura)

    AnswerHelpRequestCommand(repositories, message_service).execute(
        AnswerHelpRequestCommandDTO(help_request_id=help_request.id, text="¡Sí!", sign_as_owner=True)
    )

    assert message_service.sent[0]["text"] == "Soy Cris 😊 ¡Sí!"


def test_empty_answer_is_rejected(repositories, salon, message_service):
    help_request = help_request_for("tg:555", salon.laura)

    with pytest.raises(EmptyAnswer):
        AnswerHelpRequestCommand(repositories, message_service).execute(
            AnswerHelpRequestCommandDTO(help_request_id=help_request.id, text="  ")
        )


def test_telegram_down_keeps_the_question_open(repositories, salon):
    help_request = help_request_for("tg:555", salon.laura)

    with pytest.raises(MessageNotSent):
        AnswerHelpRequestCommand(repositories, FakeMessageService(fail=True)).execute(
            AnswerHelpRequestCommandDTO(help_request_id=help_request.id, text="¡Sí!")
        )

    help_request.refresh_from_db()
    assert help_request.status == HelpRequest.OPEN
    assert not ChatMessage.objects.exists()
