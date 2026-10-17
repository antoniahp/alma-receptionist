from datetime import timedelta

from django.utils import timezone

from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from application.queries.get_next_available_slots.query import GetNextAvailableSlotsQuery
from application.queries.get_next_available_slots.query_dto import GetNextAvailableSlotsQueryDTO


class GetSlotsNearQuery:
    """Huecos cercanos a la hora que pidió la clienta: primero el mismo día, luego los siguientes."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        wanted = timezone.localtime(dto.wanted)
        same_day = GetAvailableSlotsQuery(self.repositories).execute(
            GetAvailableSlotsQueryDTO(service_id=dto.service_id, day=wanted.date(), exclude_appointment_id=dto.exclude_appointment_id)
        )
        same_day.sort(key=lambda slot: abs((slot - wanted).total_seconds()))
        picks = sorted(same_day[: dto.count])
        if len(picks) < dto.count:
            more = GetNextAvailableSlotsQuery(self.repositories).execute(
                GetNextAvailableSlotsQueryDTO(
                    service_id=dto.service_id, count=dto.count - len(picks), from_day=wanted.date() + timedelta(days=1)
                )
            )
            picks.extend(more)
        return picks
