"""¿Es de fiar una tienda del comparador? ¿Y el enlace que nos han dado lleva de verdad a su web?

De confianza son las tiendas grandes y conocidas de esta lista y la web oficial de nuestros proveedores
(por ejemplo, la de Germaine de Capuccini). El resto se enseñan aparte como "sin verificar".
"""

import re
from urllib.parse import urlparse

from domain.rules.text_normalizer import normalize_text

# Nombre (como lo escribe Google Shopping) -> dominios en los que tiene que estar su página
TRUSTED_STORES = {
    "amazon": ["amazon.es", "amazon.com", "amazon.fr", "amazon.de", "amazon.it"],
    "aliexpress": ["aliexpress.com", "aliexpress.us", "es.aliexpress.com"],
    "el corte ingles": ["elcorteingles.es"],
    "druni": ["druni.es"],
    "primor": ["primor.eu"],
    "notino": ["notino.es", "notino.com"],
    "lookfantastic": ["lookfantastic.es", "lookfantastic.com"],
    "sephora": ["sephora.es"],
    "douglas": ["douglas.es"],
    "perfumerias if": ["perfumeriasif.com"],
    "arenal": ["arenal.com"],
    "maquillalia": ["maquillalia.com"],
    "makeup": ["makeup.es"],
    "atida": ["atida.com"],
    "promofarma": ["promofarma.com"],
    "dosfarma": ["dosfarma.com"],
    "mifarma": ["mifarma.es"],
    "carrefour": ["carrefour.es"],
    "fnac": ["fnac.es"],
    "bixoto": ["bixoto.com"],
    "cocooncenter": ["cocooncenter.es", "cocooncenter.com"],
    "farmacia imperial": ["farmaciaimperial.es", "farmaciaimperial.com"],
}


def letters_only(text):
    return re.sub(r"[^a-z0-9]", "", normalize_text(text))


def known_store(store):
    """La clave de TRUSTED_STORES que corresponde a esa tienda, o None."""
    name = normalize_text(store)
    for key in TRUSTED_STORES:
        if key in name:
            return key
    return None


def is_trusted_store(store, suppliers):
    if known_store(store):
        return True
    store_name = letters_only(store)
    return any(letters_only(supplier.name) and letters_only(supplier.name) in store_name for supplier in suppliers)


def is_trusted_link(store, link, suppliers):
    """El enlace tiene que ser https y estar en el dominio de esa tienda (o en el de la marca, si es su web oficial)."""
    try:
        url = urlparse(link)
    except ValueError:
        return False
    host = (url.hostname or "").lower()
    if url.scheme != "https" or not host:
        return False
    key = known_store(store)
    if key:
        return any(host == domain or host.endswith("." + domain) for domain in TRUSTED_STORES[key])
    for supplier in suppliers:
        brand = letters_only(supplier.name)
        if brand and brand in letters_only(store) and brand in letters_only(host):
            return True
    return False


def amazon_cart_link(items):
    """Un solo enlace que mete todos los productos de Amazon en el carrito (con sus unidades).

    items: lista de (enlace, unidades). Solo vale para enlaces de Amazon con el código del producto (ASIN).
    """
    asins = []
    host = ""
    for link, units in items:
        match = re.search(r"amazon\.([a-z.]+)/(?:.*/)?(?:dp|gp/product)/([A-Z0-9]{10})", link or "")
        if not match:
            return ""
        host = f"www.amazon.{match.group(1)}"
        asins.append((match.group(2), units))
    if not asins:
        return ""
    params = "&".join(f"ASIN.{n}={asin}&Quantity.{n}={units}" for n, (asin, units) in enumerate(asins, start=1))
    return f"https://{host}/gp/aws/cart/add.html?{params}"
