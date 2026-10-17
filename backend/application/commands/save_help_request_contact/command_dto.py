from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SaveHelpRequestContactCommandDTO:
    help_request_id: UUID
    phone: str
