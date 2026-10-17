from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UndoCompleteAppointmentCommandDTO:
    appointment_id: UUID
