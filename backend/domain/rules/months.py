"""Cuentas por meses: primer día de un mes y el mes anterior o siguiente."""

from datetime import date


def first_day(day):
    return date(day.year, day.month, 1)


def next_month(month):
    if month.month == 12:
        return date(month.year + 1, 1, 1)
    return date(month.year, month.month + 1, 1)


def previous_month(month):
    if month.month == 1:
        return date(month.year - 1, 12, 1)
    return date(month.year, month.month - 1, 1)
