"""Formato de fechas y precios (en español o en inglés, según el idioma activo) sin depender del locale del sistema."""

from datetime import date, datetime
from decimal import Decimal

from django.utils import timezone

from domain.rules.language import is_english

DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
DAYS_SHORT = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def _local(dt):
    return timezone.localtime(dt) if isinstance(dt, datetime) and timezone.is_aware(dt) else dt


def day_names():
    return DAYS_EN if is_english() else DAYS


def hour(dt):
    return _local(dt).strftime("%H:%M")


def day_long(d):
    d = _local(d)
    if is_english():
        return f"{DAYS_EN[d.weekday()]} {d.day} {MONTHS_EN[d.month - 1]}"
    return f"{DAYS[d.weekday()]} {d.day} de {MONTHS[d.month - 1]}"


def day_short(d):
    d = _local(d)
    if is_english():
        return f"{DAYS_EN[d.weekday()][:3]} {d.day}/{d.month}"
    return f"{DAYS_SHORT[d.weekday()]} {d.day}/{d.month}"


def relative_day(d):
    d = _local(d)
    day = d.date() if isinstance(d, datetime) else d
    delta = (day - timezone.localdate()).days
    english = is_english()
    if delta == 0:
        return "today" if english else "hoy"
    if delta == 1:
        return "tomorrow" if english else "mañana"
    if 1 < delta < 7:
        return f"on {DAYS_EN[day.weekday()]}" if english else f"el {DAYS[day.weekday()]}"
    if english:
        return f"on {DAYS_EN[day.weekday()]} {day.day} {MONTHS_EN[day.month - 1]}"
    return f"el {DAYS[day.weekday()]} {day.day} de {MONTHS[day.month - 1]}"


def when(dt):
    """'mañana a las 17:00', 'el jueves a las 10:30' / 'tomorrow at 17:00'."""
    return f"{relative_day(dt)} {'at' if is_english() else 'a las'} {hour(dt)}"


def button_label(dt):
    return f"{day_short(dt)} · {hour(dt)}"


def euros(value):
    value = Decimal(value)
    if is_english():
        return f"€{int(value)}" if value == value.to_integral() else f"€{value:.2f}"
    # Espacio que no se parte: el "€" nunca se queda solo en otra línea
    if value == value.to_integral():
        return f"{int(value)}\u00a0€"
    return f"{value:.2f}\u00a0€".replace(".", ",")


def as_date(value) -> date:
    return value if isinstance(value, date) and not isinstance(value, datetime) else _local(value).date()
