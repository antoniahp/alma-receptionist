import pytest
from model_bakery import baker

from application.commands.cancel_appointment.command import CancelAppointmentCommand
from application.commands.cancel_appointment.command_dto import CancelAppointmentCommandDTO
from domain.entities import Appointment, Notification
from domain.exceptions import AppointmentNotActive

pytestmark = pytest.mark.django_db


def test_cancels_and_can_notify_owner(repositories, salon, message_service):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage)

    CancelAppointmentCommand(repositories, message_service).execute(
        CancelAppointmentCommandDTO(appointment_id=appointment.id, notify_owner=True)
    )

    appointment.refresh_from_db()
    assert appointment.status == Appointment.CANCELLED
    assert Notification.objects.filter(kind=Notification.OWNER).exists()


def test_completed_appointment_cannot_be_cancelled(repositories, salon, message_service):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, status=Appointment.COMPLETED)

    with pytest.raises(AppointmentNotActive):
        CancelAppointmentCommand(repositories, message_service).execute(CancelAppointmentCommandDTO(appointment_id=appointment.id))
