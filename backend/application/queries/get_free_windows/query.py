from application.shared import schedule
from domain.rules.availability_calculator import calculate_free_windows


class GetFreeWindowsQuery:
    """Franjas libres de un día, sin importar el servicio."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return calculate_free_windows(
            open_ranges=schedule.opening_ranges(self.repositories, dto.day),
            busy_ranges=schedule.busy_ranges(self.repositories, dto.day),
            earliest=schedule.earliest_bookable_time(),
        )
