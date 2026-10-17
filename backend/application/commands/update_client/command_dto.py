from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateClientCommandDTO:
    client_id: UUID
    name: str
    phone: str
    email: str
    notes: str
    accepts_reminders: bool
