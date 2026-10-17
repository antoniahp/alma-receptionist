"""Idioma en el que habla la recepcionista con la clienta (español por defecto, inglés si escribe desde la web en inglés).

Se guarda en una ContextVar: la vista lo activa al recibir el mensaje y todos los textos de esa respuesta
(mensajes, fechas, botones) salen en ese idioma sin tener que pasarlo de función en función.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

SPANISH = "es"
ENGLISH = "en"

_current = ContextVar("language", default=SPANISH)


def normalize(value):
    return ENGLISH if (value or "").lower().startswith(ENGLISH) else SPANISH


def current():
    return _current.get()


def is_english():
    return _current.get() == ENGLISH


@contextmanager
def use(value):
    token = _current.set(normalize(value))
    try:
        yield
    finally:
        _current.reset(token)


def pick(spanish, english):
    """El texto que toca según el idioma activo: pick('Otro día', 'Another day')."""
    return english if is_english() else spanish


def in_spanish(function):
    """Para los textos de la dueña: siempre en español, hable en el idioma que hable la clienta."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        with use(SPANISH):
            return function(*args, **kwargs)

    return wrapper


def service_name(service):
    """Nombre del tratamiento en el idioma activo (en inglés solo si tiene traducción)."""
    if is_english() and getattr(service, "name_en", ""):
        return service.name_en
    return service.name


def service_description(service):
    if is_english() and getattr(service, "description_en", ""):
        return service.description_en
    return service.description
