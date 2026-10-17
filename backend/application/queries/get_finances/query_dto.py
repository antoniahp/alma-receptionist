from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GetFinancesQueryDTO:
    month: date  # cualquier día del mes que se quiere ver
    months_of_history: int = 6
