"""Textos de un tratamiento en el idioma de la petición (cabecera Accept-Language)."""

from django.utils import translation


def wants_english():
    return (translation.get_language() or "").startswith("en")


def localized(service, field):
    """service.name o service.name_en según el idioma; si no hay traducción, el texto en español."""
    if wants_english():
        translated = getattr(service, f"{field}_en", "")
        if translated:
            return translated
    return getattr(service, field)
