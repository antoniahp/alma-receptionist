from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from domain.entities import Appointment, StockMovement
from domain.exceptions import CannotUndo

# Tiempo para arrepentirse de haber pulsado "Completar"
UNDO_WINDOW = timedelta(minutes=10)


class UndoCompleteAppointmentCommand:
    """Deshace "Completar" pulsado por error: devuelve el producto al stock y la sesión al bono."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        with transaction.atomic():
            appointment = self.repositories.appointments.get_for_update(dto.appointment_id)
            if appointment.status != Appointment.COMPLETED or appointment.completed_at is None:
                raise CannotUndo("Esta cita no está completada.")
            if timezone.now() - appointment.completed_at > UNDO_WINDOW:
                raise CannotUndo()

            for movement in self.repositories.products.movements_for_appointment(appointment):
                self.repositories.products.change_stock(
                    movement.product, -movement.change, StockMovement.REASON_UNDO, appointment=appointment
                )

            if appointment.pack_id:
                pack = self.repositories.packs.get_for_update(appointment.pack_id)
                pack.sessions_used -= 1
                self.repositories.packs.save(pack, ["sessions_used"])
                appointment.pack = None

            appointment.status = Appointment.BOOKED
            appointment.payment_method = ""
            appointment.completed_at = None
            self.repositories.appointments.save(appointment, ["status", "payment_method", "pack", "completed_at"])
        return appointment
