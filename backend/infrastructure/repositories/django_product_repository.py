from django.db.models import F

from domain.entities import Product, StockMovement
from domain.repositories.product_repository import ProductRepository


class DjangoProductRepository(ProductRepository):
    def get(self, product_id):
        return Product.objects.select_related("supplier").get(pk=product_id)

    def list_with_supplier(self):
        return list(Product.objects.select_related("supplier"))

    def change_stock(self, product, uses, reason, appointment=None, order=None):
        # F() hace la suma en la base de datos: no se pierden cambios si dos citas se completan a la vez
        Product.objects.filter(pk=product.pk).update(stock_uses=F("stock_uses") + uses)
        StockMovement.objects.create(product=product, change=uses, reason=reason, appointment=appointment, order=order)

    def create(self, name, supplier, unit_price, uses_per_unit, stock_uses, min_uses, reference=""):
        return Product.objects.create(
            name=name,
            supplier=supplier,
            unit_price=unit_price,
            uses_per_unit=uses_per_unit,
            stock_uses=stock_uses,
            min_uses=min_uses,
            reference=reference,
        )

    def movements_for_appointment(self, appointment):
        return list(
            StockMovement.objects.select_related("product").filter(appointment=appointment, reason=StockMovement.REASON_APPOINTMENT)
        )
