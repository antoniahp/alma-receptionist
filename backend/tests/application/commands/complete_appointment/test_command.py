import pytest
from model_bakery import baker

from application.commands.complete_appointment.command import CompleteAppointmentCommand
from application.commands.complete_appointment.command_dto import CompleteAppointmentCommandDTO
from domain.entities import Appointment, StockMovement
from domain.exceptions import AppointmentNotActive

pytestmark = pytest.mark.django_db


def test_uses_product_stock(repositories, salon):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage)

    completed, used = CompleteAppointmentCommand(repositories).execute(CompleteAppointmentCommandDTO(appointment_id=appointment.id))

    salon.oil.refresh_from_db()
    assert completed.status == Appointment.COMPLETED
    assert salon.oil.stock_uses == 3
    assert used == [{"product": "Aceite de almendras", "uses": 1}]
    assert StockMovement.objects.get().change == -1


def test_cannot_complete_twice(repositories, salon):
    appointment = baker.make(Appointment, client=salon.laura, service=salon.massage)
    CompleteAppointmentCommand(repositories).execute(CompleteAppointmentCommandDTO(appointment_id=appointment.id))

    with pytest.raises(AppointmentNotActive):
        CompleteAppointmentCommand(repositories).execute(CompleteAppointmentCommandDTO(appointment_id=appointment.id))

    salon.oil.refresh_from_db()
    assert salon.oil.stock_uses == 3
