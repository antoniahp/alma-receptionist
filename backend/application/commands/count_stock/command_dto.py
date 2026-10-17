from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CountStockCommandDTO:
    product_id: UUID
    uses_in_stock: int
