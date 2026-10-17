from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateSupplierEmailCommandDTO:
    supplier_id: UUID
    email: str
