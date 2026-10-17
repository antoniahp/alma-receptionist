from django.conf import settings

from application.shared import schedule
from domain.rules.availability_calculator import calculate_free_slots


class GetAvailableSlotsQuery:
    """Horas libres de un día en las que cabe el servicio entero."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        service = self.repositories.services.get(dto.service_id)
        return calculate_free_slots(
            open_ranges=schedule.opening_ranges(self.repositories, dto.day),
            busy_ranges=schedule.busy_ranges(self.repositories, dto.day, dto.exclude_appointment_id),
            duration_minutes=service.duration_minutes,
            step_minutes=settings.SLOT_STEP_MINUTES,
            earliest=schedule.earliest_bookable_time(),
        )
