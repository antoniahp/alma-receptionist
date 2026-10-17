from datetime import timedelta
from decimal import Decimal

from application.shared.schedule import start_of_day
from domain.entities import Appointment, payment


class GetCashDayQuery:
    """La caja de un día: lo cobrado en efectivo, tarjeta y Bizum (citas y bonos vendidos) y si ya se cerró."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        start = start_of_day(dto.day)
        end = start + timedelta(days=1)
        totals = {payment.CASH: Decimal("0"), payment.CARD: Decimal("0"), payment.BIZUM: Decimal("0")}
        sessions_with_pack = 0
        # Cada cobro del día, para ver cómo ha pagado cada clienta
        charges = []

        completed = self.repositories.appointments.list_between(start, end, [Appointment.COMPLETED])
        for appointment in completed:
            if appointment.payment_method == payment.PACK:
                sessions_with_pack += 1
            else:
                totals[appointment.payment_method or payment.CASH] += appointment.cashed_amount
            charges.append(
                {
                    "time": appointment.start,
                    "client_name": appointment.client.name,
                    "concept": appointment.service.name,
                    "payment_method": appointment.payment_method or payment.CASH,
                    "amount": appointment.cashed_amount,
                }
            )

        packs_sold = self.repositories.packs.list_sold_between(start, end)
        for pack in packs_sold:
            totals[pack.payment_method] += pack.price
            charges.append(
                {
                    "time": pack.sold_at,
                    "client_name": pack.client.name,
                    "concept": f"Bono de {pack.sessions_total} × {pack.service.name}",
                    "payment_method": pack.payment_method,
                    "amount": pack.price,
                }
            )

        return {
            "day": dto.day,
            "cash": totals[payment.CASH],
            "card": totals[payment.CARD],
            "bizum": totals[payment.BIZUM],
            "total": sum(totals.values(), Decimal("0")),
            "appointments": len(completed),
            "sessions_with_pack": sessions_with_pack,
            "packs_sold": len(packs_sold),
            "charges": sorted(charges, key=lambda charge: charge["time"]),
            "closing": self.repositories.cash_closings.find_for_day(dto.day),
        }
