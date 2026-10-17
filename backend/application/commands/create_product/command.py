from django.db import transaction

from domain.exceptions import InvalidProductData


class CreateProductCommand:
    """La dueña añade un producto nuevo (por ejemplo, bandas de depilación) para poder pedirlo en el futuro.

    Ella piensa en unidades ("tengo 3 paquetes"); el inventario cuenta usos (cada paquete da X usos).
    """

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        name = dto.name.strip()
        if len(name) < 2:
            raise InvalidProductData("Escribe el nombre del producto.")
        if dto.unit_price < 0 or dto.uses_per_unit < 1 or dto.units_in_stock < 0 or dto.min_units < 0:
            raise InvalidProductData("Revisa el precio y las cantidades: no pueden ser negativos y cada unidad da al menos un uso.")
        if dto.supplier_id is None and not dto.new_supplier_name.strip():
            raise InvalidProductData("Elige un proveedor o escribe el nombre de uno nuevo.")

        with transaction.atomic():
            if dto.supplier_id:
                supplier = self.repositories.suppliers.get(dto.supplier_id)
            else:
                supplier = self.repositories.suppliers.create(dto.new_supplier_name.strip())
            product = self.repositories.products.create(
                name=name[:160],
                supplier=supplier,
                unit_price=dto.unit_price,
                uses_per_unit=dto.uses_per_unit,
                stock_uses=dto.units_in_stock * dto.uses_per_unit,
                min_uses=dto.min_units * dto.uses_per_unit,
            )
            for service_id in dto.service_ids:
                self.repositories.services.add_consumption(self.repositories.services.get(service_id), product, uses=1)
        return product
