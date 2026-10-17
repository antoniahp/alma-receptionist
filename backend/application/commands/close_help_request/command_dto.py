from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CloseHelpRequestCommandDTO:
    help_request_id: UUID
