from decimal import Decimal

from domain.entities import Appointment


class GetClientFileQuery:
    """Ficha de una clienta: sus datos y notas, sus citas y sus bonos."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        client = self.repositories.clients.get(dto.client_id)
        appointments = self.repositories.appointments.list_for_client(client.id)
        completed = [appointment for appointment in appointments if appointment.status == Appointment.COMPLETED]
        packs = self.repositories.packs.list_for_client(client.id)
        spent = sum((appointment.cashed_amount for appointment in completed), Decimal("0")) + sum(
            (pack.price for pack in packs), Decimal("0")
        )
        return {
            "client": client,
            "appointments": appointments,
            "packs": packs,
            "visits": len(completed),
            "spent": spent,
        }
