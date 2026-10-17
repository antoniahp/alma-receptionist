from django.db import transaction
from django.utils import timezone

from domain.entities import Appointment, StockMovement, payment
from domain.exceptions import InvalidPayment, NoActivePack


class CompleteAppointmentCommand:
    """Marca la cita como completada, apunta cómo se ha pagado y descuenta del stock lo que gasta el servicio.

    Si se paga con bono, se gasta una sesión del bono (el dinero ya entró al venderlo).
    """

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        if dto.payment_method not in dict(payment.METHODS):
            raise InvalidPayment()
        with transaction.atomic():
            appointment = self.repositories.appointments.get_for_update(dto.appointment_id)
            appointment.ensure_active()

            if dto.payment_method == payment.PACK:
                pack = self.repositories.packs.find_active_for_update(appointment.client_id, appointment.service_id)
                if pack is None:
                    raise NoActivePack()
                pack.sessions_used += 1
                self.repositories.packs.save(pack, ["sessions_used"])
                appointment.pack = pack

            used = []
            for item in self.repositories.services.list_consumption(appointment.service):
                self.repositories.products.change_stock(item.product, -item.uses, StockMovement.REASON_APPOINTMENT, appointment=appointment)
                used.append({"product": item.product.name, "uses": item.uses})

            appointment.status = Appointment.COMPLETED
            appointment.payment_method = dto.payment_method
            appointment.completed_at = timezone.now()
            self.repositories.appointments.save(appointment, ["status", "payment_method", "pack", "completed_at"])
        return appointment, used
