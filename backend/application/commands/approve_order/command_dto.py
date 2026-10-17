from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ApproveOrderCommandDTO:
    order_id: UUID
