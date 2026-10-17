from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CloseCashCommandDTO:
    day: date
    counted_cash: Decimal
    notes: str = ""
