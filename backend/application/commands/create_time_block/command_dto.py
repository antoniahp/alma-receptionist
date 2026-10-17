from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateTimeBlockCommandDTO:
    start: datetime
    end: datetime
    reason: str = ""
