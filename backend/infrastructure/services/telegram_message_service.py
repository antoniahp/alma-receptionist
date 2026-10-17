"""Adaptador de Telegram (Bot API) usando requests, sin librerías extra."""

import requests
from django.conf import settings

from domain.exceptions import MessageNotSent
from domain.services.message_service import MessageService

API_URL = "https://api.telegram.org/bot{token}/{method}"


class TelegramMessageService(MessageService):
    def __init__(self, token=None):
        self.token = token if token is not None else settings.TELEGRAM_BOT_TOKEN

    def is_enabled(self):
        return bool(self.token)

    def call(self, method, params, request_timeout=15):
        """Llama a la Bot API. 'params' va a Telegram; 'request_timeout' es cuánto esperamos la respuesta."""
        if not self.is_enabled():
            raise MessageNotSent("Falta TELEGRAM_BOT_TOKEN.")
        try:
            response = requests.post(API_URL.format(token=self.token, method=method), json=params, timeout=request_timeout)
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            raise MessageNotSent(f"Telegram no responde: {error}") from error
        if not data.get("ok"):
            raise MessageNotSent(data.get("description", "Error de Telegram"))
        return data["result"]

    def send(self, chat_id, text, buttons=None):
        params = {"chat_id": chat_id, "text": text}
        if buttons:
            keyboard = []
            for row in buttons:
                keyboard.append([{"text": button.label, "callback_data": button.data} for button in row])
            params["reply_markup"] = {"inline_keyboard": keyboard}
        result = self.call("sendMessage", params)
        return str(result.get("message_id", ""))

    def send_typing(self, chat_id):
        try:
            self.call("sendChatAction", {"chat_id": chat_id, "action": "typing"}, request_timeout=5)
        except MessageNotSent:
            pass

    def answer_button(self, callback_id):
        try:
            self.call("answerCallbackQuery", {"callback_query_id": callback_id})
        except MessageNotSent:
            pass

    def remove_buttons(self, chat_id, message_id):
        try:
            self.call("editMessageReplyMarkup", {"chat_id": chat_id, "message_id": message_id, "reply_markup": {"inline_keyboard": []}})
        except MessageNotSent:
            pass

    def get_updates(self, offset=None, timeout=25):
        params = {"timeout": timeout, "allowed_updates": ["message", "callback_query"]}
        if offset is not None:
            params["offset"] = offset
        # Telegram espera hasta 'timeout' segundos a que llegue algo; nosotros esperamos un poco más
        return self.call("getUpdates", params, request_timeout=timeout + 10)


def telegram_deep_link(client):
    """Enlace para que la clienta abra el bot y quede vinculada a su ficha."""
    username = settings.TELEGRAM_BOT_USERNAME.lstrip("@")
    if not username:
        return ""
    return f"https://t.me/{username}?start={client.telegram_link_code}"
