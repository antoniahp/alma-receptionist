import pytest

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from application.queries.get_stock_forecast.query import GetStockForecastQuery
from application.queries.get_stock_forecast.query_dto import GetStockForecastQueryDTO
from domain.entities.product_forecast import STATUS_ORDER
from tests.helpers import local_datetime

pytestmark = pytest.mark.django_db


def test_counts_what_booked_appointments_will_use(repositories, salon, next_monday, message_service):
    for hour in (10, 11, 12):
        BookAppointmentCommand(repositories, message_service).execute(
            BookAppointmentCommandDTO(
                client_id=salon.laura.id, service_id=salon.massage.id, start=local_datetime(next_monday, hour), source="owner"
            )
        )

    forecast = GetStockForecastQuery(repositories).execute(GetStockForecastQueryDTO())[0]

    assert forecast.product == salon.oil
    assert forecast.reserved == 3
    assert forecast.after_bookings == 1
    assert forecast.status == STATUS_ORDER
