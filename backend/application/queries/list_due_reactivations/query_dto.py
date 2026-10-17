from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ListDueReactivationsQueryDTO:
    today: date | None = None
    days_ahead: int = 2
