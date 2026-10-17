from dataclasses import dataclass


@dataclass(frozen=True)
class ListConversationsQueryDTO:
    limit: int = 20
    messages_per_conversation: int = 6
