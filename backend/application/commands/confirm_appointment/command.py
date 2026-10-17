from domain.entities import Appointment


class ConfirmAppointmentCommand:
    """La clienta confirma que vendrá (botón del recordatorio)."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        appointment = self.repositories.appointments.get(dto.appointment_id)
        appointment.ensure_active()
        appointment.status = Appointment.CONFIRMED
        self.repositories.appointments.save(appointment, ["status"])
        return appointment
