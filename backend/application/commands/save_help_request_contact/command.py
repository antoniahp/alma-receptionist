from application.commands.notify_owner.command import NotifyOwnerCommand
from application.commands.notify_owner.command_dto import NotifyOwnerCommandDTO
from domain.rules import customer_messages
from domain.rules.phone_format import clean_phone


class SaveHelpRequestContactCommand:
    """La clienta de la web deja su teléfono por si cierra el chat antes de recibir respuesta."""

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        help_request = self.repositories.help_requests.get(dto.help_request_id)
        phone = clean_phone(dto.phone)
        help_request.contact = phone
        # Si al dar el móvil hemos reconocido a la clienta, la pregunta queda también en su ficha
        if help_request.client is None and help_request.conversation.client:
            help_request.client = help_request.conversation.client
        self.repositories.help_requests.save(help_request, ["contact", "client"])
        client = help_request.client
        if client and not client.phone:
            client.phone = phone
            self.repositories.clients.save(client, ["phone"])
        client_name = client.name if client else "La clienta"
        NotifyOwnerCommand(self.repositories, self.message_service).execute(
            NotifyOwnerCommandDTO(text=customer_messages.owner_phone_left(client_name, phone), client_id=help_request.client_id)
        )
        return help_request
