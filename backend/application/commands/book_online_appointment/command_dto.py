from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BookOnlineAppointmentCommandDTO:
    service_id: UUID
    start: datetime
    name: str
    phone: str = ""
    privacy_accepted: bool = False
