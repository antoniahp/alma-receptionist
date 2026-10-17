from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class ListAppointmentsQueryDTO:
    date_from: date | None = None
    date_to: date | None = None
    statuses: list = field(default_factory=list)
