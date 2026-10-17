from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GetCashDayQueryDTO:
    day: date
