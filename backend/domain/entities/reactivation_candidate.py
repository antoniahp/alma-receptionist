from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class ReactivationCandidate:
    """Clienta a la que le toca repetir un tratamiento."""

    client: object
    service: object
    last_visit: datetime
    days_since: int
    due: date
    days_until_due: int
