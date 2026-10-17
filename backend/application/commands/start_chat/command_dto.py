from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class StartChatCommandDTO:
    conversation_key: str
    client_id: UUID | None = None
