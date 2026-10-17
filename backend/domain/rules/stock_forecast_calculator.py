"""Regla pura de previsión de stock: cuánto quedará tras las citas reservadas y si hay que pedir."""

import math

from domain.entities.product_forecast import STATUS_OK, STATUS_ORDER, STATUS_ORDERED, STATUS_WATCH, ProductForecast


def calculate_product_forecast(product, upcoming_uses, already_ordered):
    """upcoming_uses: lista de (cita, usos) en orden de fecha."""
    left = product.stock_uses
    reserved = 0
    runs_out_for = None
    for appointment, uses in upcoming_uses:
        reserved += uses
        left -= uses
        if left < 0 and runs_out_for is None:
            runs_out_for = appointment

    if left < product.min_uses:
        status = STATUS_ORDER
    elif left <= product.min_uses * 1.5:
        status = STATUS_WATCH
    else:
        status = STATUS_OK

    if status != STATUS_OK and already_ordered:
        status = STATUS_ORDERED

    suggested_units = 0
    if status in (STATUS_ORDER, STATUS_ORDERED):
        missing_uses = max(0, product.min_uses - left)
        suggested_units = math.ceil(missing_uses / product.uses_per_unit) + 1

    return ProductForecast(
        product=product,
        stock=product.stock_uses,
        reserved=reserved,
        after_bookings=left,
        status=status,
        suggested_units=suggested_units,
        runs_out_for=runs_out_for,
    )
