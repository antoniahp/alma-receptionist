from domain.entities import Appointment


class MarkNoShowCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        appointment = self.repositories.appointments.get(dto.appointment_id)
        appointment.ensure_active()
        appointment.status = Appointment.NO_SHOW
        self.repositories.appointments.save(appointment, ["status"])
        return appointment
