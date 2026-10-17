from dataclasses import dataclass

STATUS_OK = "ok"
STATUS_WATCH = "watch"
STATUS_ORDER = "order"
STATUS_ORDERED = "ordered"


@dataclass(frozen=True)
class ProductForecast:
    """Cómo queda un producto después de atender las citas ya reservadas."""

    product: object
    stock: int
    reserved: int
    after_bookings: int
    status: str
    suggested_units: int
    runs_out_for: object | None
