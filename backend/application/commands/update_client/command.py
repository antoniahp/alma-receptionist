from application.commands.create_client.command import check_client_data
from domain.exceptions import DuplicatedClient
from domain.rules.phone_format import clean_phone


class UpdateClientCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        client = self.repositories.clients.get(dto.client_id)
        email = dto.email.strip().lower()
        check_client_data(dto.name, email)
        phone = clean_phone(dto.phone)
        if phone:
            existing = self.repositories.clients.find_by_phone(phone)
            if existing and existing.id != client.id:
                raise DuplicatedClient(f"Ya tienes a {existing.name} con ese teléfono.")
        client.name = dto.name.strip()[:120]
        client.phone = phone
        client.email = email
        client.notes = dto.notes.strip()
        client.accepts_reminders = dto.accepts_reminders
        self.repositories.clients.save(client, ["name", "phone", "email", "notes", "accepts_reminders"])
        return client
