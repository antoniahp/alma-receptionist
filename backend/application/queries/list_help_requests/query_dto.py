from dataclasses import dataclass, field


@dataclass(frozen=True)
class ListHelpRequestsQueryDTO:
    statuses: list = field(default_factory=list)
    limit: int = 50
