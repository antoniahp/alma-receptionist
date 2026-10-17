import pytest

from application.commands.answer_help_request.command import AnswerHelpRequestCommand
from application.commands.answer_help_request.command_dto import AnswerHelpRequestCommandDTO
from domain.entities import HelpRequest
from tests.fakes import FakeMessageService

pytestmark = pytest.mark.django_db


def test_owner_answer_reaches_the_web_chat(repositories, api_client, salon):
    first = api_client.post("/api/public/chat/", {"message": "¿Hacéis micropigmentación?"}, format="json").json()
    session, last_id = first["session"], first["last_id"]

    nothing_yet = api_client.get("/api/public/chat/updates/", {"session": session, "after": last_id}).json()
    AnswerHelpRequestCommand(repositories, FakeMessageService()).execute(
        AnswerHelpRequestCommandDTO(help_request_id=HelpRequest.objects.get().id, text="¡Sí!")
    )
    updates = api_client.get("/api/public/chat/updates/", {"session": session, "after": last_id}).json()

    assert nothing_yet == []
    assert [update["text"] for update in updates] == ["¡Sí!"]
    assert api_client.get("/api/public/chat/updates/", {"session": session, "after": updates[0]["id"]}).json() == []
