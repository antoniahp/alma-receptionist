from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker

from application.commands.send_reactivation.command import SendReactivationCommand
from application.commands.send_reactivation.command_dto import SendReactivationCommandDTO
from domain.entities import Appointment, Notification
from domain.exceptions import ReactivationNotDue
from tests.fakes import FakeLanguageModelService

pytestmark = pytest.mark.django_db


def visited_long_ago(salon):
    baker.make(
        Appointment, client=salon.laura, service=salon.massage, status=Appointment.COMPLETED, start=timezone.now() - timedelta(days=31)
    )


def test_sends_template_with_slot_buttons(repositories, salon, message_service, language_model_service):
    visited_long_ago(salon)

    notification = SendReactivationCommand(repositories, message_service, language_model_service).execute(
        SendReactivationCommandDTO(client_id=salon.laura.id, service_id=salon.massage.id)
    )

    assert notification.kind == Notification.REACTIVATION
    assert notification.text.startswith("¡Hola, Laura!")


def test_uses_ai_text_when_it_looks_right(repositories, salon, message_service):
    visited_long_ago(salon)
    language_model_service = FakeLanguageModelService(text_response="¡Hola Laura! Ya te toca masaje, ¿te guardo el jueves a las 10:00?")

    notification = SendReactivationCommand(repositories, message_service, language_model_service).execute(
        SendReactivationCommandDTO(client_id=salon.laura.id, service_id=salon.massage.id)
    )

    assert notification.text == "¡Hola Laura! Ya te toca masaje, ¿te guardo el jueves a las 10:00?"


def test_not_sent_if_not_due(repositories, salon, message_service, language_model_service):
    with pytest.raises(ReactivationNotDue):
        SendReactivationCommand(repositories, message_service, language_model_service).execute(
            SendReactivationCommandDTO(client_id=salon.laura.id, service_id=salon.massage.id)
        )
