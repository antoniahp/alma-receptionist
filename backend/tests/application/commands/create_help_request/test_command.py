import pytest
from model_bakery import baker

from application.commands.create_help_request.command import CreateHelpRequestCommand
from application.commands.create_help_request.command_dto import CreateHelpRequestCommandDTO
from domain.entities import Conversation, HelpRequest
from tests.fakes import FakeMessageService

pytestmark = pytest.mark.django_db


def test_notifies_owner_and_remembers_message_id(repositories, salon):
    conversation = baker.make(Conversation, key="tg:555", client=salon.laura)
    message_service = FakeMessageService()

    help_request = CreateHelpRequestCommand(repositories, message_service).execute(
        CreateHelpRequestCommandDTO(conversation_id=conversation.id, question="¿Láser?")
    )

    assert message_service.sent[0]["chat_id"] == "999"
    assert help_request.owner_message_id == "101"


def test_second_question_is_added_to_the_open_one(repositories, salon, message_service):
    conversation = baker.make(Conversation, key="tg:555", client=salon.laura)
    command = CreateHelpRequestCommand(repositories, message_service)

    command.execute(CreateHelpRequestCommandDTO(conversation_id=conversation.id, question="¿Láser?"))
    command.execute(CreateHelpRequestCommandDTO(conversation_id=conversation.id, question="¿Y precio?"))

    assert HelpRequest.objects.get().question == "¿Láser?\n¿Y precio?"
