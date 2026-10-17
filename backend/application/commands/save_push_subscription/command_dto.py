from dataclasses import dataclass


@dataclass(frozen=True)
class SavePushSubscriptionCommandDTO:
    endpoint: str
    p256dh: str
    auth: str
