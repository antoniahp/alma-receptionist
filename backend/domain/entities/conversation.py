import uuid

from django.db import models

from domain.entities.base_model import BaseModel


class Conversation(BaseModel):
    """Conversación con la recepcionista. La clave es 'tg:<chat_id>' (Telegram) o 'web:<uuid>' (web)."""

    TELEGRAM_PREFIX = "tg:"
    WEB_PREFIX = "web:"

    key = models.CharField(max_length=80, unique=True)
    client = models.ForeignKey("domain.Client", null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations")
    state = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    @property
    def channel(self):
        return "telegram" if self.key.startswith(self.TELEGRAM_PREFIX) else "web"

    @property
    def telegram_chat_id(self):
        if self.channel != "telegram":
            return None
        return self.key[len(self.TELEGRAM_PREFIX) :]

    def get_state(self, name):
        return (self.state or {}).get(name)

    def set_state(self, **values):
        """Cambia valores del estado. None borra el valor. Hay que guardarlo con el repositorio."""
        state = dict(self.state or {})
        for name, value in values.items():
            if value is None:
                state.pop(name, None)
            elif isinstance(value, uuid.UUID):
                state[name] = str(value)  # el estado se guarda como JSON
            else:
                state[name] = value
        self.state = state


class ChatMessage(BaseModel):
    USER = "user"
    ASSISTANT = "assistant"
    ROLES = [(USER, "Clienta"), (ASSISTANT, "Recepcionista")]

    conversation = models.ForeignKey("domain.Conversation", on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLES)
    text = models.TextField()
    by_ai = models.BooleanField(default=False)
    from_owner = models.BooleanField(default=False, help_text="Lo escribió la dueña desde el panel o Telegram")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
