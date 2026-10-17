from django.db import transaction
from django.utils import timezone

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from domain.entities import Appointment
from domain.exceptions import DomainError, PrivacyNotAccepted
from domain.rules.phone_format import clean_phone


class BookOnlineAppointmentCommand:
    """Reserva desde la página pública: busca a la clienta por teléfono o la crea."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        name = dto.name.strip()
        phone = clean_phone(dto.phone)
        if len(name) < 2:
            raise DomainError("Dinos tu nombre.")
        if not dto.privacy_accepted:
            raise PrivacyNotAccepted()

        # Si la reserva falla, la ficha de la clienta nueva tampoco se guarda
        with transaction.atomic():
            client = self.repositories.clients.find_by_phone(phone)
            if client is None:
                client = self.repositories.clients.create(name=name[:120], phone=phone[:30])
            client.privacy_accepted_at = timezone.now()
            self.repositories.clients.save(client, ["privacy_accepted_at"])
            return BookAppointmentCommand(self.repositories, self.message_service).execute(
                BookAppointmentCommandDTO(client_id=client.id, service_id=dto.service_id, start=dto.start, source=Appointment.SOURCE_WEB)
            )
