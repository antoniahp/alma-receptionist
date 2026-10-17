from dataclasses import dataclass


@dataclass(frozen=True)
class DeletePushSubscriptionCommandDTO:
    endpoint: str
