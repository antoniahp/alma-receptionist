from django.db import transaction


class LinkTelegramChatCommand:
    """Encuentra la clienta de un chat de Telegram.

    - Si llega con el código de su enlace de reserva (/start <código>), une el chat a su ficha.
    - Si no la conocemos, crea una ficha con su nombre de Telegram.
    """

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        chat_id = str(dto.chat_id)
        with transaction.atomic():
            client = self.repositories.clients.find_by_telegram_chat(chat_id)
            linked = self.repositories.clients.find_by_link_code(dto.link_code)
            if linked and linked != client:
                if client:
                    client.telegram_chat_id = None
                    self.repositories.clients.save(client, ["telegram_chat_id"])
                linked.telegram_chat_id = chat_id
                self.repositories.clients.save(linked, ["telegram_chat_id"])
                return linked
            if client is None:
                name = f"{dto.first_name} {dto.last_name}".strip() or "Clienta"
                client = self.repositories.clients.create(name=name[:120], telegram_chat_id=chat_id)
        return client
