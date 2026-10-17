from dataclasses import dataclass, field


@dataclass(frozen=True)
class ListPurchaseOrdersQueryDTO:
    statuses: list = field(default_factory=list)
