from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class RescheduleAppointmentCommandDTO:
    appointment_id: UUID
    new_start: datetime
    notify_owner: bool = True
