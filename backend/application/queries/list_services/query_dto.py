from dataclasses import dataclass


@dataclass(frozen=True)
class ListServicesQueryDTO:
    only_active: bool = False
