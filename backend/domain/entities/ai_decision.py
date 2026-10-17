from dataclasses import dataclass

ACTION_NONE = "none"
ACTION_OFFER_SLOTS = "offer_slots"
ACTION_BOOK = "book"
ACTION_CANCEL = "cancel"
ACTION_HANDOFF = "handoff"
ACTIONS = [ACTION_NONE, ACTION_OFFER_SLOTS, ACTION_BOOK, ACTION_CANCEL, ACTION_HANDOFF]


@dataclass(frozen=True)
class AiDecision:
    """Lo que propone el modelo: el texto para la clienta y una acción que el sistema valida antes de ejecutar."""

    reply: str
    action: str = ACTION_NONE
    service_id: str | None = None
    date: str | None = None
    part_of_day: str | None = None
    start: str | None = None
    appointment_id: str | None = None
    client_name: str | None = None

    @classmethod
    def from_dict(cls, data):
        action = data.get("action") or {}
        # Por si el modelo se salta el esquema y manda la acción como texto ("book") en vez de objeto
        if not isinstance(action, dict):
            action = {"type": action} if isinstance(action, str) else {}
        action_type = action.get("type") if action.get("type") in ACTIONS else ACTION_NONE
        return cls(
            reply=str(data.get("reply") or "").strip(),
            action=action_type,
            service_id=action.get("service_id"),
            date=action.get("date"),
            part_of_day=action.get("part_of_day"),
            start=action.get("start"),
            appointment_id=action.get("appointment_id"),
            client_name=action.get("client_name"),
        )
