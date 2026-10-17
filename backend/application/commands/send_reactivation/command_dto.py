from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SendReactivationCommandDTO:
    client_id: UUID
    service_id: UUID
