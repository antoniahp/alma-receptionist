from dataclasses import dataclass


@dataclass(frozen=True)
class ListClientsQueryDTO:
    search: str = ""
