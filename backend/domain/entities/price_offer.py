from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PriceOffer:
    """Una tienda que vende el producto a un precio. No se guarda en la base de datos."""

    store: str
    title: str
    price: Decimal
    link: str
    # Para pedir el enlace directo a la tienda (cuesta una búsqueda, así que solo se pide al pulsar)
    page_token: str = ""
    # Tienda conocida o web oficial de un proveedor
    trusted: bool = False
