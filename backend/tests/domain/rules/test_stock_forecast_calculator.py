from types import SimpleNamespace

from domain.entities.product_forecast import STATUS_OK, STATUS_ORDER, STATUS_ORDERED, STATUS_WATCH
from domain.rules.stock_forecast_calculator import calculate_product_forecast


def product(stock, minimum=3, uses_per_unit=5):
    return SimpleNamespace(stock_uses=stock, min_uses=minimum, uses_per_unit=uses_per_unit)


def test_orders_when_bookings_leave_stock_below_minimum():
    forecast = calculate_product_forecast(product(stock=4), [("cita1", 1), ("cita2", 1), ("cita3", 1)], already_ordered=False)

    assert forecast.reserved == 3
    assert forecast.after_bookings == 1
    assert forecast.status == STATUS_ORDER
    assert forecast.suggested_units == 2


def test_marks_who_runs_out():
    forecast = calculate_product_forecast(product(stock=1), [("ana", 1), ("marta", 1)], already_ordered=False)

    assert forecast.runs_out_for == "marta"


def test_watch_status_near_minimum():
    forecast = calculate_product_forecast(product(stock=4), [], already_ordered=False)

    assert forecast.status == STATUS_WATCH


def test_ok_with_plenty_of_stock():
    forecast = calculate_product_forecast(product(stock=20), [("cita", 1)], already_ordered=False)

    assert forecast.status == STATUS_OK
    assert forecast.suggested_units == 0


def test_ordered_status_when_there_is_an_open_order():
    forecast = calculate_product_forecast(product(stock=0), [], already_ordered=True)

    assert forecast.status == STATUS_ORDERED
