from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DiscardOrderCommandDTO:
    order_id: UUID
