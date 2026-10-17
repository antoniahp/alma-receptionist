from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class AddToShoppingListCommandDTO:
    product_id: UUID
    store: str
    title: str
    price: Decimal
    link: str
    units: int
    page_token: str = ""
