from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetClientFileQueryDTO:
    client_id: UUID
