from datetime import datetime

from domain.entities.time_range import TimeRange
from domain.rules.availability_calculator import calculate_free_slots, calculate_free_windows


def at(hour, minute=0):
    return datetime(2030, 1, 7, hour, minute)


MORNING = TimeRange(at(10), at(14))


def test_slots_fit_whole_service_before_closing():
    slots = calculate_free_slots([MORNING], [], duration_minutes=60, step_minutes=30, earliest=at(0))

    assert slots[0] == at(10)
    assert slots[-1] == at(13)


def test_slots_skip_busy_ranges():
    busy = [TimeRange(at(10), at(11))]

    slots = calculate_free_slots([MORNING], busy, duration_minutes=60, step_minutes=30, earliest=at(0))

    assert at(10) not in slots
    assert at(10, 30) not in slots
    assert at(11) in slots


def test_slots_respect_earliest_time():
    slots = calculate_free_slots([MORNING], [], duration_minutes=60, step_minutes=30, earliest=at(12))

    assert slots == [at(12), at(12, 30), at(13)]


def test_free_windows_split_around_appointments():
    busy = [TimeRange(at(11), at(12))]

    windows = calculate_free_windows([MORNING], busy, earliest=at(0))

    assert windows == [TimeRange(at(10), at(11)), TimeRange(at(12), at(14))]


def test_free_windows_round_up_to_half_hour():
    windows = calculate_free_windows([MORNING], [], earliest=at(10, 10))

    assert windows == [TimeRange(at(10, 30), at(14))]
