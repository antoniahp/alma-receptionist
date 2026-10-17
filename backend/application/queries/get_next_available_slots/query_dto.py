from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class GetNextAvailableSlotsQueryDTO:
    service_id: UUID
    count: int = 3
    from_day: date | None = None
    one_per_day: bool = True
