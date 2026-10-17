from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class ChatButton:
    label: str
    data: str


@dataclass
class ChatReply:
    """Respuesta de la recepcionista: texto, botones opcionales (filas) y la cita creada si la hubo."""

    text: str
    buttons: list = field(default_factory=list)
    appointment_id: UUID | None = None
    by_ai: bool = False
