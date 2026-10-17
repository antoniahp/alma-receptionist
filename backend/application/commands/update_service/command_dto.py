from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class UpdateServiceCommandDTO:
    service_id: UUID
    name: str
    category: str
    price: Decimal
    duration_minutes: int
    active: bool
    description: str = ""
    name_en: str = ""
    description_en: str = ""
    repeat_every_days: int | None = None
