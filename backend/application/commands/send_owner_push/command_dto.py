from dataclasses import dataclass


@dataclass(frozen=True)
class SendOwnerPushCommandDTO:
    title: str
    body: str
    url: str = "/panel"
