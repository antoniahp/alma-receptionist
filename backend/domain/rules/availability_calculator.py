"""Reglas puras para calcular huecos libres. No acceden a la base de datos."""

from datetime import timedelta

from domain.entities.time_range import TimeRange


def calculate_free_slots(open_ranges, busy_ranges, duration_minutes, step_minutes, earliest):
    """Horas de inicio en las que cabe el servicio completo sin pisar ninguna cita."""
    duration = timedelta(minutes=duration_minutes)
    step = timedelta(minutes=step_minutes)
    slots = []
    for open_range in open_ranges:
        start = open_range.start
        while start + duration <= open_range.end:
            candidate = TimeRange(start, start + duration)
            is_busy = any(candidate.overlaps(busy) for busy in busy_ranges)
            if start >= earliest and not is_busy:
                slots.append(start)
            start += step
    return slots


def round_up_to_half_hour(moment):
    moment = moment.replace(second=0, microsecond=0)
    if moment.minute % 30 == 0:
        return moment
    return moment + timedelta(minutes=30 - moment.minute % 30)


def calculate_free_windows(open_ranges, busy_ranges, earliest):
    """Franjas libres de un día (sin citas). Se usan para dar contexto a la IA."""
    busy_sorted = sorted(busy_ranges, key=lambda busy: busy.start)
    windows = []
    for open_range in open_ranges:
        cursor = round_up_to_half_hour(max(open_range.start, earliest))
        if cursor >= open_range.end:
            continue
        for busy in busy_sorted:
            if busy.end <= cursor or busy.start >= open_range.end:
                continue
            if busy.start > cursor:
                windows.append(TimeRange(cursor, min(busy.start, open_range.end)))
            cursor = max(cursor, busy.end)
        if cursor < open_range.end:
            windows.append(TimeRange(cursor, open_range.end))
    return windows
