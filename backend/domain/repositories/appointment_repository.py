from abc import ABC, abstractmethod


class AppointmentRepository(ABC):
    @abstractmethod
    def get(self, appointment_id):
        """Devuelve la cita o lanza Appointment.DoesNotExist."""

    @abstractmethod
    def get_for_update(self, appointment_id):
        """Como get, pero bloquea la fila hasta que termine la transacción."""

    @abstractmethod
    def find_active_for_client(self, appointment_id, client_id):
        """Cita activa de esa clienta o None."""

    @abstractmethod
    def create(self, client, service, start, source, notes=""):
        pass

    @abstractmethod
    def save(self, appointment, fields):
        pass

    @abstractmethod
    def list_active_between(self, start, end, exclude_appointment_id=None):
        """Citas activas que empiezan entre start y end."""

    @abstractmethod
    def list_active_since(self, since):
        """Citas activas desde una fecha, con su servicio y lo que gasta, por orden de hora."""

    @abstractmethod
    def list_without_reminder_between(self, start, end):
        """Citas activas entre start y end que aún no tienen recordatorio."""

    @abstractmethod
    def list_between(self, start=None, end=None, statuses=None):
        pass

    @abstractmethod
    def list_upcoming_for_client(self, client_id, since):
        pass

    @abstractmethod
    def last_completed_for_client(self, client_id):
        pass

    @abstractmethod
    def last_completed_visits(self):
        """Última visita completada por clienta y servicio (solo servicios que se repiten y clientas que aceptan avisos).

        Devuelve una lista de dicts con client_id, service_id y last_visit.
        """

    @abstractmethod
    def booked_client_service_pairs_since(self, since):
        """Conjunto de (client_id, service_id) con una cita activa desde esa fecha."""

    @abstractmethod
    def list_for_client(self, client_id, limit=30):
        """Historial de citas de una clienta, la más reciente primero."""
