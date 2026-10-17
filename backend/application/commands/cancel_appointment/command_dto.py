from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CancelAppointmentCommandDTO:
    appointment_id: UUID
    notify_owner: bool = False
