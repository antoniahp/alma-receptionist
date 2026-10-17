"""Teléfonos escritos siempre igual, para poder buscarlos y no repetir clientas."""

import re


def clean_phone(phone):
    """'600123456', '600-12-34-56' o '+34 600 123 456' -> '600 123 456' (o '+34 600 123 456')."""
    digits = re.sub(r"\D", "", phone or "")
    prefix = ""
    if phone and phone.strip().startswith("+") and len(digits) > 9:
        prefix, digits = f"+{digits[:-9]} ", digits[-9:]
    if len(digits) == 9:
        return f"{prefix}{digits[0:3]} {digits[3:6]} {digits[6:9]}"
    return (phone or "").strip()[:30]
