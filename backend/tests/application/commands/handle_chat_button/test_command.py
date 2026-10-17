import pytest
from model_bakery import baker

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from application.commands.handle_chat_button.command import HandleChatButtonCommand
from application.commands.handle_chat_button.command_dto import HandleChatButtonCommandDTO
from domain.entities import Appointment
from infrastructure.repositories.django_repositories import build_django_repositories
from tests.helpers import button_data, local_datetime

pytestmark = pytest.mark.django_db


def press(message_service, data, client_id):
    repositories = build_django_repositories()
    return HandleChatButtonCommand(repositories, message_service).execute(
        HandleChatButtonCommandDTO(conversation_key="tg:555", data=data, client_id=client_id)
    )


@pytest.fixture
def appointment(repositories, salon, next_monday, message_service):
    return BookAppointmentCommand(repositories, message_service).execute(
        BookAppointmentCommandDTO(
            client_id=salon.laura.id, service_id=salon.massage.id, start=local_datetime(next_monday, 10), source="owner"
        )
    )


def test_confirm_from_reminder(salon, appointment, message_service):
    press(message_service, f"confirm:{appointment.id}", salon.laura.id)

    appointment.refresh_from_db()
    assert appointment.status == Appointment.CONFIRMED


def test_change_and_move(salon, appointment, message_service):
    original_start = appointment.start
    reply = press(message_service, f"change:{appointment.id}", salon.laura.id)
    move = next(data for data in button_data(reply) if data.startswith("move:"))

    reply = press(message_service, move, salon.laura.id)

    appointment.refresh_from_db()
    assert "Cambiado" in reply.text
    assert appointment.start != original_start


def test_cancel_from_chat(salon, appointment, message_service):
    press(message_service, f"cancel:{appointment.id}", salon.laura.id)

    appointment.refresh_from_db()
    assert appointment.status == Appointment.CANCELLED


def test_cannot_touch_someone_elses_appointment(salon, appointment, message_service):
    stranger = baker.make("domain.Client", name="Otra")

    reply = press(message_service, f"cancel:{appointment.id}", stranger.id)

    appointment.refresh_from_db()
    assert appointment.status == Appointment.BOOKED
    assert "No encuentro" in reply.text


def test_unknown_button(salon, message_service):
    assert "no he entendido" in press(message_service, "rubbish", salon.laura.id).text


def test_malformed_buttons_do_not_crash(salon, message_service):
    for data in ["slot:", "slot:abc:xyz", "move:1", "more:", "svc:999", "confirm:abc"]:
        assert press(message_service, data, salon.laura.id).text
