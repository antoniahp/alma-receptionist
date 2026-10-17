from django.utils import timezone

from domain.entities import payment
from domain.exceptions import InvalidPack, InvalidPayment

MIN_SESSIONS = 2
MAX_SESSIONS = 50


class SellPackCommand:
    """La dueña vende un bono: se cobra hoy y luego cada cita se paga con una sesión."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        if not MIN_SESSIONS <= dto.sessions <= MAX_SESSIONS or dto.price < 0:
            raise InvalidPack()
        if dto.payment_method not in payment.PACK_SALE_METHODS:
            raise InvalidPayment("Un bono se cobra en efectivo, tarjeta o Bizum.")
        client = self.repositories.clients.get(dto.client_id)
        service = self.repositories.services.get(dto.service_id)
        return self.repositories.packs.create(
            client=client,
            service=service,
            sessions_total=dto.sessions,
            price=dto.price,
            payment_method=dto.payment_method,
            sold_at=timezone.now(),
        )
