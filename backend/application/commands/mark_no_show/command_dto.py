from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class MarkNoShowCommandDTO:
    appointment_id: UUID
