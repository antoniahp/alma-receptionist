from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class AddExpenseCommandDTO:
    concept: str
    category: str
    amount: Decimal
    date: date
