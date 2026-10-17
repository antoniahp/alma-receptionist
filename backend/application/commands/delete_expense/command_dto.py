from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteExpenseCommandDTO:
    expense_id: UUID
