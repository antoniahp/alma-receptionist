from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ListDueRemindersQueryDTO:
    now: datetime | None = None
