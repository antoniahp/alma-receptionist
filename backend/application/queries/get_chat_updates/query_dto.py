from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetChatUpdatesQueryDTO:
    session: str
    after_message_id: UUID | None = None
