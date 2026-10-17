"""Traduce cada mensaje de Telegram en el command de aplicación que toca."""

import logging

from django.conf import settings

from application.commands.answer_help_request.command import AnswerHelpRequestCommand
from application.commands.answer_help_request.command_dto import AnswerHelpRequestCommandDTO
from application.commands.handle_chat_button.command import HandleChatButtonCommand
from application.commands.handle_chat_button.command_dto import HandleChatButtonCommandDTO
from application.commands.handle_chat_message.command import HandleChatMessageCommand
from application.commands.handle_chat_message.command_dto import HandleChatMessageCommandDTO
from application.commands.link_telegram_chat.command import LinkTelegramChatCommand
from application.commands.link_telegram_chat.command_dto import LinkTelegramChatCommandDTO
from application.commands.start_chat.command import StartChatCommand
from application.commands.start_chat.command_dto import StartChatCommandDTO
from domain.entities import Conversation
from domain.exceptions import DomainError
from domain.rules import customer_messages

logger = logging.getLogger(__name__)
ONLY_TEXT_MESSAGE = "De momento solo leo mensajes de texto, ¿me lo escribes? 😊"


class TelegramUpdateHandler:
    def __init__(self, repositories, telegram, language_model_service):
        self.repositories = repositories
        self.telegram = telegram
        self.language_model_service = language_model_service

    def handle(self, update):
        if "callback_query" in update:
            self.handle_button(update["callback_query"])
            return
        message = update.get("message")
        if not message:
            return
        chat_id = str(message["chat"]["id"])
        if "text" not in message:
            self.telegram.send(chat_id, ONLY_TEXT_MESSAGE)
            return
        is_owner = settings.TELEGRAM_OWNER_CHAT_ID and chat_id == str(settings.TELEGRAM_OWNER_CHAT_ID)
        # Si la dueña abre el enlace de una clienta (/start <código>), la tratamos como esa clienta.
        # Así puede probar los recordatorios con su propio Telegram.
        opens_client_link = message["text"].startswith("/start ")
        if is_owner and not opens_client_link:
            self.handle_owner_message(message)
            return
        self.handle_client_message(message)

    def link_client(self, chat, link_code=None):
        return LinkTelegramChatCommand(self.repositories).execute(
            LinkTelegramChatCommandDTO(
                chat_id=str(chat["id"]),
                first_name=chat.get("first_name", ""),
                last_name=chat.get("last_name", ""),
                link_code=link_code,
            )
        )

    def handle_client_message(self, message):
        chat = message["chat"]
        chat_id = str(chat["id"])
        text = message["text"].strip()
        key = f"{Conversation.TELEGRAM_PREFIX}{chat_id}"

        if text.startswith("/start"):
            parts = text.split(maxsplit=1)
            link_code = parts[1] if len(parts) > 1 else None
            client = self.link_client(chat, link_code)
            reply = StartChatCommand(self.repositories, self.telegram).execute(
                StartChatCommandDTO(conversation_key=key, client_id=client.id)
            )
        else:
            client = self.link_client(chat)
            self.telegram.send_typing(chat_id)
            reply = HandleChatMessageCommand(self.repositories, self.telegram, self.language_model_service).execute(
                HandleChatMessageCommandDTO(conversation_key=key, text=text, client_id=client.id)
            )
        self.telegram.send(chat_id, reply.text, reply.buttons)

    def handle_button(self, callback):
        message = callback.get("message") or {}
        chat = message.get("chat") or callback["from"]
        chat_id = str(chat["id"])
        client = self.link_client(chat)
        self.telegram.answer_button(callback["id"])
        if message.get("message_id"):
            self.telegram.remove_buttons(chat_id, message["message_id"])
        reply = HandleChatButtonCommand(self.repositories, self.telegram).execute(
            HandleChatButtonCommandDTO(
                conversation_key=f"{Conversation.TELEGRAM_PREFIX}{chat_id}", data=callback.get("data", ""), client_id=client.id
            )
        )
        self.telegram.send(chat_id, reply.text, reply.buttons)

    def handle_owner_message(self, message):
        """La dueña responde a un aviso: se lo hacemos llegar a la clienta."""
        chat_id = str(message["chat"]["id"])
        replied_to = (message.get("reply_to_message") or {}).get("message_id")
        help_request = None
        if replied_to:
            help_request = self.repositories.help_requests.find_by_owner_message_id(replied_to)
        if help_request is None:
            pending = self.repositories.help_requests.count_open()
            self.telegram.send(chat_id, customer_messages.owner_reply_how_to(pending))
            return
        try:
            AnswerHelpRequestCommand(self.repositories, self.telegram).execute(
                AnswerHelpRequestCommandDTO(help_request_id=help_request.id, text=message["text"])
            )
        except DomainError as error:
            self.telegram.send(chat_id, f"⚠️ {error}")
            return
        client_name = help_request.client.name if help_request.client else "la clienta"
        self.telegram.send(chat_id, f"✅ Enviado a {client_name}.")
