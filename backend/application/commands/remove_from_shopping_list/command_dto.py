from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveFromShoppingListCommandDTO:
    item_id: UUID
