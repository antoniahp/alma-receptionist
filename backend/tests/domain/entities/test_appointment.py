import pytest
from model_bakery import baker

from domain.entities import Appointment
from domain.exceptions import AppointmentNotActive
from tests.helpers import local_datetime


@pytest.mark.django_db
def test_end_uses_service_duration(salon, next_monday):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, start=local_datetime(next_monday, 10))

    assert appointment.end == local_datetime(next_monday, 11)


@pytest.mark.django_db
def test_cancelled_appointment_is_not_active(salon):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage, status=Appointment.CANCELLED)

    with pytest.raises(AppointmentNotActive):
        appointment.ensure_active()
