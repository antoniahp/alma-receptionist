from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO


class GetNextAvailableSlotsQuery:
    """Primeros huecos libres a partir de un día. Por defecto uno por día, alternando mañana y tarde."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        day = dto.from_day or timezone.localdate()
        slots_query = GetAvailableSlotsQuery(self.repositories)
        found = []
        for _ in range(settings.BOOKING_DAYS_AHEAD):
            day_slots = slots_query.execute(GetAvailableSlotsQueryDTO(service_id=dto.service_id, day=day))
            if day_slots:
                if dto.one_per_day:
                    if len(found) % 2 == 0:
                        found.append(day_slots[0])
                    else:
                        found.append(day_slots[len(day_slots) // 2])
                else:
                    found.extend(day_slots[: dto.count - len(found)])
            if len(found) >= dto.count:
                break
            day += timedelta(days=1)
        return found[: dto.count]
