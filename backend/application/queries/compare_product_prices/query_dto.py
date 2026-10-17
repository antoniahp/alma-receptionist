from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompareProductPricesQueryDTO:
    product_id: UUID
