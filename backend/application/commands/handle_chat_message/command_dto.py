from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class HandleChatMessageCommandDTO:
    conversation_key: str
    text: str
    client_id: UUID | None = None
