from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class SellPackCommandDTO:
    client_id: UUID
    service_id: UUID
    sessions: int
    price: Decimal
    payment_method: str
