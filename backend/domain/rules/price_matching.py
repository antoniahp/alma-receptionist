"""¿Una oferta de una tienda es el mismo producto que el nuestro?

Comparamos las palabras importantes del nombre (marca, línea, tipo de producto). Las cantidades
("30 ml", "800") y las palabras cortas no cuentan, porque las tiendas las escriben de muchas formas.
"""

import re

from domain.rules.text_normalizer import normalize_text

MIN_SHARED_WORDS = 0.7
# Tiendas de segunda mano: no sirven para comprar producto profesional
SECOND_HAND_STORES = ("wallapop", "vinted", "milanuncios")
IGNORED_WORDS = {"para", "con", "sin", "por", "los", "las", "del", "una", "uno", "unidad", "unidades", "pack", "surtido"}


def important_words(text):
    words = re.findall(r"[a-z0-9]+", normalize_text(text))
    return {
        word
        for word in words
        if len(word) > 2 and not word.isdigit() and word not in IGNORED_WORDS and not re.fullmatch(r"\d+(ml|g|l|kg|gr)", word)
    }


def sizes(text):
    """Tamaños que aparecen en el texto, por ejemplo {'100ml', '800ml'}."""
    found = re.findall(r"(\d+)\s*(ml|g|gr|l)\b", normalize_text(text))
    return {f"{number}{'g' if unit == 'gr' else unit}" for number, unit in found}


def is_same_product(product_name, offer_title):
    wanted = important_words(product_name)
    if not wanted:
        return False
    # Si los dos dicen tamaño y no coincide, es otro formato (40 ml no es más barato que 100 ml)
    wanted_sizes = sizes(product_name)
    offer_sizes = sizes(offer_title)
    if wanted_sizes and offer_sizes and not wanted_sizes & offer_sizes:
        return False
    found = wanted & important_words(offer_title)
    return len(found) / len(wanted) >= MIN_SHARED_WORDS


def is_second_hand(store):
    return any(name in normalize_text(store) for name in SECOND_HAND_STORES)


def supplier_for_store(suppliers, store):
    """El proveedor que corresponde a una tienda del comparador ('Germaine de Capuccini' en su web oficial), o None."""
    store_name = normalize_text(store)
    for supplier in suppliers:
        supplier_name = normalize_text(supplier.name)
        if supplier_name and (supplier_name in store_name or store_name in supplier_name):
            return supplier
    return None
