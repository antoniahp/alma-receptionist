from dataclasses import dataclass
from uuid import UUID

from domain.entities import payment


@dataclass(frozen=True)
class CompleteAppointmentCommandDTO:
    appointment_id: UUID
    payment_method: str = payment.CASH
