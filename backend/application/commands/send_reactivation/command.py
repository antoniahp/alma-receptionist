from django.conf import settings
from django.utils import timezone

from application.commands.send_message_to_client.command import SendMessageToClientCommand
from application.commands.send_message_to_client.command_dto import SendMessageToClientCommandDTO
from application.queries.get_next_available_slots.query import GetNextAvailableSlotsQuery
from application.queries.get_next_available_slots.query_dto import GetNextAvailableSlotsQueryDTO
from application.queries.list_due_reactivations.query import ListDueReactivationsQuery
from application.queries.list_due_reactivations.query_dto import ListDueReactivationsQueryDTO
from domain.entities import Notification
from domain.entities.chat_reply import ChatButton
from domain.exceptions import LanguageModelUnavailable, ReactivationNotDue
from domain.rules import customer_messages
from domain.rules import spanish_format as fmt


class SendReactivationCommand:
    """Mensaje para que la clienta repita su tratamiento, con botones de huecos libres."""

    def __init__(self, repositories, message_service, language_model_service):
        self.repositories = repositories
        self.message_service = message_service
        self.language_model_service = language_model_service

    def execute(self, dto):
        candidates = ListDueReactivationsQuery(self.repositories).execute(ListDueReactivationsQueryDTO())
        candidate = None
        for item in candidates:
            if item.client.id == dto.client_id and item.service.id == dto.service_id:
                candidate = item
        if candidate is None:
            raise ReactivationNotDue()

        slots = GetNextAvailableSlotsQuery(self.repositories).execute(
            GetNextAvailableSlotsQueryDTO(service_id=candidate.service.id, count=3)
        )
        buttons = []
        for slot in slots:
            buttons.append([ChatButton(fmt.button_label(slot), f"slot:{candidate.service.id}:{timezone.localtime(slot):%Y%m%d%H%M}")])
        buttons.append([ChatButton("Ahora no, gracias", "later")])

        return SendMessageToClientCommand(self.repositories, self.message_service).execute(
            SendMessageToClientCommandDTO(
                client_id=candidate.client.id,
                kind=Notification.REACTIVATION,
                text=self.write_text(candidate, slots),
                buttons=buttons,
                service_id=candidate.service.id,
            )
        )

    def write_text(self, candidate, slots):
        """La IA local lo personaliza; si no está disponible, usamos la plantilla."""
        template = customer_messages.reactivation_text(candidate, slots)
        if not slots:
            return template
        prompt = (
            f"Eres {settings.BUSINESS['assistant_name']}, de recepción en el centro de estética {settings.BUSINESS['name']}. "
            f"Escribe un mensaje de Telegram corto (máx. 45 palabras), cercano y natural en español de España, para {candidate.client.first_name}. "
            f"Su último {candidate.service.name.lower()} fue hace {candidate.days_since} días y se recomienda repetir cada "
            f"{candidate.service.repeat_every_days} días. Ofrece estos huecos: {', '.join(fmt.when(slot) for slot in slots[:2])}. "
            "Pregunta si le guardas uno. Nada de presión comercial ni descuentos. Como mucho un emoji. Devuelve solo el mensaje."
        )
        try:
            text = self.language_model_service.write_text(prompt, temperature=0.8)
        except LanguageModelUnavailable:
            return template
        looks_right = candidate.client.first_name.lower() in text.lower() and 20 < len(text) < 500
        return text if looks_right else template
