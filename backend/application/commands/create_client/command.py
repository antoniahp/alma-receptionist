from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from domain.exceptions import DuplicatedClient, InvalidClientData
from domain.rules.phone_format import clean_phone


def check_client_data(name, email):
    """Comprobaciones comunes al dar de alta y al editar."""
    if len(name.strip()) < 2:
        raise InvalidClientData("Escribe el nombre de la clienta.")
    if email:
        try:
            validate_email(email)
        except ValidationError as error:
            raise InvalidClientData("Ese correo no es válido.") from error


class CreateClientCommand:
    """La dueña da de alta una clienta a mano (por ejemplo, alguien que llama por teléfono)."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        email = dto.email.strip().lower()
        check_client_data(dto.name, email)
        phone = clean_phone(dto.phone)
        if phone:
            existing = self.repositories.clients.find_by_phone(phone)
            if existing:
                raise DuplicatedClient(f"Ya tienes a {existing.name} con ese teléfono.")
        return self.repositories.clients.create(name=dto.name.strip()[:120], phone=phone, email=email, notes=dto.notes.strip())
