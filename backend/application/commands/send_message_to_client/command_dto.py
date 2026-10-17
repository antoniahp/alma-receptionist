from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class SendMessageToClientCommandDTO:
    client_id: UUID
    kind: str
    text: str
    buttons: list = field(default_factory=list)
    appointment_id: UUID | None = None
    service_id: UUID | None = None
