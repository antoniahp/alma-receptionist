import unicodedata


def normalize_text(text):
    """Minúsculas y sin tildes, para comparar lo que escribe la clienta con palabras clave."""
    text = unicodedata.normalize("NFD", (text or "").lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")
