from dataclasses import dataclass


@dataclass(frozen=True)
class OrderFromStoreCommandDTO:
    store: str
    # True: ya lo ha comprado ella en la web de la tienda. False: preparar un correo al proveedor.
    bought_online: bool
