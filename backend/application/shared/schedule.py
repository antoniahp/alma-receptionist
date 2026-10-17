"""Pasa el horario y las citas de un día al formato que usan las reglas de dominio."""

from datetime import datetime, timedelta

from django.utils import timezone

from domain.entities.time_range import TimeRange


def make_local_datetime(day, time_of_day):
    return timezone.make_aware(datetime.combine(day, time_of_day))


def start_of_day(day):
    return make_local_datetime(day, datetime.min.time())


def opening_ranges(repositories, day):
    hours = repositories.opening_hours.list_for_weekday(day.weekday())
    return [TimeRange(make_local_datetime(day, h.opens), make_local_datetime(day, h.closes)) for h in hours]


def busy_ranges(repositories, day, exclude_appointment_id=None):
    # Se mira desde 12 h antes por si alguna cita del día anterior se alargara
    day_start = start_of_day(day)
    appointments = repositories.appointments.list_active_between(
        day_start - timedelta(hours=12), day_start + timedelta(days=1), exclude_appointment_id
    )
    busy = [TimeRange(appointment.start, appointment.end) for appointment in appointments]
    # Las horas que la dueña ha bloqueado (vacaciones, médico...) tampoco se pueden reservar
    blocks = repositories.time_blocks.list_overlapping(day_start, day_start + timedelta(days=1))
    return busy + [TimeRange(block.start, block.end) for block in blocks]


def earliest_bookable_time():
    """No se puede reservar con menos de 30 minutos de antelación."""
    return timezone.localtime() + timedelta(minutes=30)
