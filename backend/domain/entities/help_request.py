from django.db import models

from domain.entities.base_model import BaseModel


class HelpRequest(BaseModel):
    """Pregunta que la recepcionista no sabe contestar y pasa a la dueña."""

    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"
    STATUS = [(OPEN, "Esperando respuesta"), (ANSWERED, "Contestada"), (CLOSED, "Resuelta")]

    conversation = models.ForeignKey("domain.Conversation", on_delete=models.CASCADE, related_name="help_requests")
    client = models.ForeignKey("domain.Client", null=True, blank=True, on_delete=models.SET_NULL, related_name="help_requests")
    question = models.TextField("pregunta")
    contact = models.CharField("contacto", max_length=60, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default=OPEN)
    answer = models.TextField("respuesta", blank=True)
    owner_message_id = models.CharField(max_length=20, blank=True, help_text="Aviso enviado a la dueña por Telegram")
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "pregunta para la dueña"
        verbose_name_plural = "preguntas para la dueña"

    def __str__(self):
        return f"{self.client or 'Clienta'}: {self.question[:40]}"

    @property
    def channel(self):
        return self.conversation.channel
