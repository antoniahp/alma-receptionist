import pytest

from application.commands.book_online_appointment.command import BookOnlineAppointmentCommand
from application.commands.book_online_appointment.command_dto import BookOnlineAppointmentCommandDTO
from domain.entities import Appointment, Client
from domain.exceptions import DomainError, SlotNotAvailable
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def test_reuses_client_with_same_phone(repositories, salon, next_monday, message_service):
    appointment = BookOnlineAppointmentCommand(repositories, message_service).execute(
        BookOnlineAppointmentCommandDTO(
            service_id=salon.massage.id, start=local_datetime(next_monday, 10), name="Laura", phone="611111111", privacy_accepted=True
        )
    )

    assert appointment.client == salon.laura
    assert appointment.source == Appointment.SOURCE_WEB


def test_does_not_create_client_if_slot_is_taken(repositories, salon, next_monday, message_service):
    command = BookOnlineAppointmentCommand(repositories, message_service)
    command.execute(
        BookOnlineAppointmentCommandDTO(
            service_id=salon.massage.id, start=local_datetime(next_monday, 10), name="Ana Torres", phone="677", privacy_accepted=True
        )
    )

    with pytest.raises(SlotNotAvailable):
        command.execute(
            BookOnlineAppointmentCommandDTO(
                service_id=salon.massage.id, start=local_datetime(next_monday, 10), name="Irene", phone="699", privacy_accepted=True
            )
        )

    assert not Client.objects.filter(name="Irene").exists()


def test_name_is_required(repositories, salon, next_monday, message_service):
    with pytest.raises(DomainError):
        BookOnlineAppointmentCommand(repositories, message_service).execute(
            BookOnlineAppointmentCommandDTO(service_id=salon.massage.id, start=local_datetime(next_monday, 10), name=" ")
        )
