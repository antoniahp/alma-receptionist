from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateServiceCommandDTO:
    name: str
    category: str
    price: Decimal
    duration_minutes: int
    description: str = ""
    name_en: str = ""
    description_en: str = ""
    repeat_every_days: int | None = None
