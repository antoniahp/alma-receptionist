from dataclasses import dataclass


@dataclass(frozen=True)
class GetStoreLinkQueryDTO:
    page_token: str
    store: str
