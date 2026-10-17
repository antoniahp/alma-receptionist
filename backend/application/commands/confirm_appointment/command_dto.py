from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ConfirmAppointmentCommandDTO:
    appointment_id: UUID
