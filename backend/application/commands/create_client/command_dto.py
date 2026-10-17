from dataclasses import dataclass


@dataclass(frozen=True)
class CreateClientCommandDTO:
    name: str
    phone: str = ""
    email: str = ""
    notes: str = ""
