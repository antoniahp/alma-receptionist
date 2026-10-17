from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class GetAvailableSlotsQueryDTO:
    service_id: UUID
    day: date
    exclude_appointment_id: UUID | None = None
