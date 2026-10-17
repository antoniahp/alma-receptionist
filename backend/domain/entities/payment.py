"""Formas de pago de una cita o de un bono."""

CASH = "efectivo"
CARD = "tarjeta"
BIZUM = "bizum"
PACK = "bono"  # la cita se paga con una sesión de un bono ya cobrado

METHODS = [(CASH, "Efectivo"), (CARD, "Tarjeta"), (BIZUM, "Bizum"), (PACK, "Bono")]
# Un bono se cobra en efectivo, tarjeta o Bizum (no con otro bono)
PACK_SALE_METHODS = [CASH, CARD, BIZUM]
