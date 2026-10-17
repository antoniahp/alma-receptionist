from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SendReminderCommandDTO:
    appointment_id: UUID
