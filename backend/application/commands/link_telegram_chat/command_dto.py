from dataclasses import dataclass


@dataclass(frozen=True)
class LinkTelegramChatCommandDTO:
    chat_id: str
    first_name: str = ""
    last_name: str = ""
    link_code: str | None = None
