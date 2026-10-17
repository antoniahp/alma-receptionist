import pytest
from model_bakery import baker

from application.commands.send_owner_push.command import SendOwnerPushCommand
from application.commands.send_owner_push.command_dto import SendOwnerPushCommandDTO
from domain.entities import PushSubscription
from tests.fakes import FakePushService

pytestmark = pytest.mark.django_db


def test_sends_to_every_browser_and_forgets_the_ones_that_left(repositories):
    baker.make(PushSubscription, endpoint="https://push.example/movil")
    baker.make(PushSubscription, endpoint="https://push.example/viejo")
    push = FakePushService(expired_endpoints={"https://push.example/viejo"})

    sent = SendOwnerPushCommand(repositories, push).execute(SendOwnerPushCommandDTO(title="Alma", body="Nueva cita"))

    assert sent == 1
    assert push.sent[0]["endpoint"] == "https://push.example/movil"
    assert list(PushSubscription.objects.values_list("endpoint", flat=True)) == ["https://push.example/movil"]


def test_without_keys_nothing_is_sent(repositories):
    baker.make(PushSubscription, endpoint="https://push.example/movil")

    assert SendOwnerPushCommand(repositories, FakePushService(enabled=False)).execute(SendOwnerPushCommandDTO(title="A", body="B")) == 0
