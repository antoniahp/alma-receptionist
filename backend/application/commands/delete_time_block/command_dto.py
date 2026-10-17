from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteTimeBlockCommandDTO:
    block_id: UUID
