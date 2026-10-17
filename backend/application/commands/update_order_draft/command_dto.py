from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateOrderDraftCommandDTO:
    order_id: UUID
    email_subject: str
    email_body: str
