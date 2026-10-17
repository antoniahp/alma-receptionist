from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreateProductCommandDTO:
    name: str
    unit_price: Decimal
    uses_per_unit: int
    units_in_stock: int
    min_units: int
    # Proveedor que ya existe, o el nombre de uno nuevo
    supplier_id: UUID | None = None
    new_supplier_name: str = ""
    # Servicios que gastan un uso de este producto cada vez
    service_ids: list[UUID] = field(default_factory=list)
