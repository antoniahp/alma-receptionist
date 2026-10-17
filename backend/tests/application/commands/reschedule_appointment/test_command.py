import pytest
from django.utils import timezone

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from application.commands.reschedule_appointment.command import RescheduleAppointmentCommand
from application.commands.reschedule_appointment.command_dto import RescheduleAppointmentCommandDTO
from domain.entities import Appointment
from domain.exceptions import SlotNotAvailable
from infrastructure.repositories.django_repositories import build_django_repositories
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def book(salon, message_service, start):
    repositories = build_django_repositories()
    return BookAppointmentCommand(repositories, message_service).execute(
        BookAppointmentCommandDTO(client_id=salon.laura.id, service_id=salon.massage.id, start=start, source="owner")
    )


def test_moves_to_free_slot_and_resets_reminder(repositories, salon, next_monday, message_service):
    appointment = book(salon, message_service, local_datetime(next_monday, 10))
    appointment.reminder_sent_at = timezone.now()
    appointment.status = Appointment.CONFIRMED
    appointment.save()

    moved = RescheduleAppointmentCommand(repositories, message_service).execute(
        RescheduleAppointmentCommandDTO(appointment_id=appointment.id, new_start=local_datetime(next_monday, 17))
    )

    assert moved.start == local_datetime(next_monday, 17)
    assert moved.status == Appointment.BOOKED
    assert moved.reminder_sent_at is None


def test_can_move_half_an_hour_over_its_own_time(repositories, salon, next_monday, message_service):
    appointment = book(salon, message_service, local_datetime(next_monday, 10))

    moved = RescheduleAppointmentCommand(repositories, message_service).execute(
        RescheduleAppointmentCommandDTO(appointment_id=appointment.id, new_start=local_datetime(next_monday, 10, 30))
    )

    assert moved.start == local_datetime(next_monday, 10, 30)


def test_cannot_move_onto_another_appointment(repositories, salon, next_monday, message_service):
    appointment = book(salon, message_service, local_datetime(next_monday, 10))
    book(salon, message_service, local_datetime(next_monday, 17))

    with pytest.raises(SlotNotAvailable):
        RescheduleAppointmentCommand(repositories, message_service).execute(
            RescheduleAppointmentCommandDTO(appointment_id=appointment.id, new_start=local_datetime(next_monday, 17))
        )
