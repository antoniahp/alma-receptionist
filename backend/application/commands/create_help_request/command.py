from application.commands.notify_owner.command import NotifyOwnerCommand
from application.commands.notify_owner.command_dto import NotifyOwnerCommandDTO
from domain.rules import customer_messages


class CreateHelpRequestCommand:
    """La recepcionista no sabe contestar: guarda la pregunta y avisa a la dueña.

    Si ya había una pregunta abierta en esa conversación, se le añade el nuevo mensaje.
    """

    def __init__(self, repositories, message_service):
        self.repositories = repositories
        self.message_service = message_service

    def execute(self, dto):
        conversation = self.repositories.conversations.get(dto.conversation_id)
        question = dto.question.strip()[:1000]
        help_request = self.repositories.help_requests.find_open_for_conversation(conversation)
        if help_request:
            help_request.question = f"{help_request.question}\n{question}"[:2000]
            self.repositories.help_requests.save(help_request, ["question"])
        else:
            contact = conversation.client.phone if conversation.client else ""
            help_request = self.repositories.help_requests.create(
                conversation=conversation, client=conversation.client, question=question, contact=contact
            )

        client_name = conversation.client.name if conversation.client else "Una clienta"
        text = customer_messages.owner_help_alert(client_name, help_request.question, conversation.channel, help_request.contact)
        notification = NotifyOwnerCommand(self.repositories, self.message_service).execute(
            NotifyOwnerCommandDTO(text=text, client_id=conversation.client_id)
        )
        if notification.telegram_message_id:
            help_request.owner_message_id = notification.telegram_message_id
            self.repositories.help_requests.save(help_request, ["owner_message_id"])
        return help_request
