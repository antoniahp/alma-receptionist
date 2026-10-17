import pytest
from model_bakery import baker

from domain.entities import ChatMessage, Conversation, HelpRequest

pytestmark = pytest.mark.django_db


def test_reply_and_close(owner_client, salon):
    conversation = baker.make(Conversation, key="web:3f0c7c52-6d33-4d8e-9a4e-2f9f6f1c2b11")
    help_request = baker.make(HelpRequest, conversation=conversation, question="¿Pedicura?")

    listed = owner_client.get("/api/help-requests/", {"status": "open"}).json()
    assert listed[0]["question"] == "¿Pedicura?"

    replied = owner_client.post(f"/api/help-requests/{help_request.id}/reply/", {"text": "¡Sí!", "sign": False}, format="json")
    assert replied.json()["status"] == "answered"
    assert ChatMessage.objects.get().from_owner

    closed = owner_client.post(f"/api/help-requests/{help_request.id}/close/")
    assert closed.json()["status"] == "closed"


def test_empty_reply_is_rejected(owner_client, salon):
    help_request = baker.make(HelpRequest, conversation=baker.make(Conversation, key="web:x"))

    response = owner_client.post(f"/api/help-requests/{help_request.id}/reply/", {"text": "  "}, format="json")

    assert response.status_code == 400
