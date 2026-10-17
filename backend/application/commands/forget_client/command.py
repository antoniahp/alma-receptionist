from django.utils import timezone

from domain.exceptions import DomainError


class ForgetClientCommand:
    """Derecho de supresión (RGPD): la clienta pide que se borren sus datos.

    Se anulan antes sus citas pendientes. Las citas pasadas se quedan sin nombre porque hacen falta para las cuentas.
    """

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        client = self.repositories.clients.get(dto.client_id)
        upcoming = self.repositories.appointments.list_upcoming_for_client(client.id, timezone.now())
        if upcoming:
            raise DomainError("Tiene citas pendientes: cancélalas antes de borrar sus datos.")
        self.repositories.clients.forget(client)
        return client
