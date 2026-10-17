from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class HandleChatButtonCommandDTO:
    conversation_key: str
    data: str
    client_id: UUID | None = None
