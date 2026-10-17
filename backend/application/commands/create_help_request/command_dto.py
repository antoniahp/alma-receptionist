from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateHelpRequestCommandDTO:
    conversation_id: UUID
    question: str
