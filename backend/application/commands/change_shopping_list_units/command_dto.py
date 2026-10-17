from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChangeShoppingListUnitsCommandDTO:
    item_id: UUID
    units: int
