from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class GetSlotsNearQueryDTO:
    service_id: UUID
    wanted: datetime
    count: int = 3
    exclude_appointment_id: UUID | None = None
