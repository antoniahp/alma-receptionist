from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class NotifyOwnerCommandDTO:
    text: str
    client_id: UUID | None = None
