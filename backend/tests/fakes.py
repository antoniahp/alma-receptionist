"""Versiones falsas de los puertos para no llamar a Telegram ni a la IA en los tests."""

from domain.exceptions import LanguageModelUnavailable, MessageNotSent, PushSubscriptionExpired
from domain.services.email_service import EmailService
from domain.services.language_model_service import LanguageModelService
from domain.services.message_service import MessageService
from domain.services.price_search_service import PriceSearchService
from domain.services.push_service import PushService


class FakeMessageService(MessageService):
    def __init__(self, enabled=True, fail=False):
        self.enabled = enabled
        self.fail = fail
        self.sent = []

    def is_enabled(self):
        return self.enabled

    def send(self, chat_id, text, buttons=None):
        if self.fail:
            raise MessageNotSent("Telegram caído")
        self.sent.append({"chat_id": str(chat_id), "text": text, "buttons": buttons or []})
        return str(100 + len(self.sent))

    # Métodos extra del cliente real de Telegram que usa el bot
    def send_typing(self, chat_id):
        pass

    def answer_button(self, callback_id):
        pass

    def remove_buttons(self, chat_id, message_id):
        pass


class FakeLanguageModelService(LanguageModelService):
    """Sin respuestas configuradas se comporta como si Ollama estuviera apagado."""

    def __init__(self, json_response=None, text_response=None):
        self.json_response = json_response
        self.text_response = text_response
        self.received = []

    def is_available(self):
        return self.json_response is not None or self.text_response is not None

    def write_text(self, prompt, temperature=0.6):
        self.received.append(prompt)
        if self.text_response is None:
            raise LanguageModelUnavailable("apagado")
        return self.text_response

    def write_json(self, messages, schema, temperature=0.6):
        self.received.append(messages)
        if self.json_response is None:
            raise LanguageModelUnavailable("apagado")
        return self.json_response


class FakeEmailService(EmailService):
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append({"to": to, "subject": subject, "body": body})


class FakePriceSearchService(PriceSearchService):
    def __init__(self, offers=None, enabled=True, links=None):
        self.offers = offers or []
        self.enabled = enabled
        self.links = links or {}
        self.queries = []

    def is_enabled(self):
        return self.enabled

    def search(self, query):
        self.queries.append(query)
        return self.offers

    def store_link(self, page_token, store):
        return self.links.get(store, "")


class FakePushService(PushService):
    def __init__(self, enabled=True, expired_endpoints=()):
        self.enabled = enabled
        self.expired_endpoints = set(expired_endpoints)
        self.sent = []

    def is_enabled(self):
        return self.enabled

    def public_key(self):
        return "clave-publica" if self.enabled else ""

    def send(self, subscription, title, body, url):
        if subscription.endpoint in self.expired_endpoints:
            raise PushSubscriptionExpired()
        self.sent.append({"endpoint": subscription.endpoint, "title": title, "body": body, "url": url})
