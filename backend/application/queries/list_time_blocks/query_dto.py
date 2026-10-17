from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ListTimeBlocksQueryDTO:
    start: datetime
    end: datetime
