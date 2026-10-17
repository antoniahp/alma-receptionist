from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SendReviewRequestsCommandDTO:
    now: datetime | None = None
