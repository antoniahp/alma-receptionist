from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AnswerHelpRequestCommandDTO:
    help_request_id: UUID
    text: str
    sign_as_owner: bool = False
