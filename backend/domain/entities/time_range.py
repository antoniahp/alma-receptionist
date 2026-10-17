from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime

    def overlaps(self, other):
        return self.start < other.end and other.start < self.end
