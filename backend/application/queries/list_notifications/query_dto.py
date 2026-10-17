from dataclasses import dataclass


@dataclass(frozen=True)
class ListNotificationsQueryDTO:
    limit: int = 100
