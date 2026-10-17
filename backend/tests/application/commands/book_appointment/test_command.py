import pytest
from django.utils import timezone

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from domain.entities import Appointment, Notification
from domain.exceptions import InvalidBookingData, SlotNotAvailable
from infrastructure.repositories.django_repositories import build_django_repositories
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def book(salon, message_service, start, source=Appointment.SOURCE_OWNER):
    repositories = build_django_repositories()
    return BookAppointmentCommand(repositories, message_service).execute(
        BookAppointmentCommandDTO(client_id=salon.laura.id, service_id=salon.massage.id, start=start, source=source)
    )


def test_books_a_free_slot(salon, next_monday, message_service):
    appointment = book(salon, message_service, local_datetime(next_monday, 10))

    assert appointment.status == Appointment.BOOKED
    assert appointment.client == salon.laura


def test_rejects_overlapping_slot(salon, next_monday, message_service):
    book(salon, message_service, local_datetime(next_monday, 11))

    with pytest.raises(SlotNotAvailable):
        book(salon, message_service, local_datetime(next_monday, 11, 30))


def test_rejects_time_outside_opening_hours(salon, next_monday, message_service):
    with pytest.raises(SlotNotAvailable):
        book(salon, message_service, local_datetime(next_monday, 13, 30))


def test_rejects_inactive_service(salon, next_monday, message_service):
    salon.massage.active = False
    salon.massage.save()

    with pytest.raises(InvalidBookingData):
        book(salon, message_service, local_datetime(next_monday, 10))


def test_owner_is_notified_of_online_bookings(salon, next_monday, message_service):
    book(salon, message_service, local_datetime(next_monday, 10), source=Appointment.SOURCE_WEB)

    notification = Notification.objects.get(kind=Notification.OWNER)
    assert "Laura Gómez" in notification.text


def test_owner_is_not_notified_of_her_own_bookings(salon, next_monday, message_service):
    book(salon, message_service, local_datetime(next_monday, 10))

    assert not Notification.objects.exists()


def test_a_booking_for_the_next_24_hours_does_not_get_a_second_reminder(repositories, salon, message_service, next_monday, monkeypatch):
    monkeypatch.setattr(timezone, "now", lambda: local_datetime(next_monday, 9))

    appointment = BookAppointmentCommand(repositories, message_service).execute(
        BookAppointmentCommandDTO(
            client_id=salon.laura.id, service_id=salon.massage.id, start=local_datetime(next_monday, 11), source=Appointment.SOURCE_WEB
        )
    )

    assert appointment.reminder_sent_at is not None


def test_a_booking_for_next_week_keeps_its_reminder_pending(repositories, salon, message_service, next_monday):
    appointment = BookAppointmentCommand(repositories, message_service).execute(
        BookAppointmentCommandDTO(
            client_id=salon.laura.id, service_id=salon.massage.id, start=local_datetime(next_monday, 11), source=Appointment.SOURCE_WEB
        )
    )

    assert appointment.reminder_sent_at is None
