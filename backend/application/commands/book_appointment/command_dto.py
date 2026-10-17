from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BookAppointmentCommandDTO:
    client_id: UUID
    service_id: UUID
    start: datetime
    source: str
    notes: str = ""
