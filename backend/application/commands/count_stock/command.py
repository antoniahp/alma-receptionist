from domain.exceptions import InvalidProductData


class CountStockCommand:
    """La dueña cuenta lo que hay en la estantería y corrige el stock. Queda apuntado como movimiento."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        if dto.uses_in_stock < 0:
            raise InvalidProductData("El stock no puede ser negativo.")
        product = self.repositories.products.get(dto.product_id)
        difference = dto.uses_in_stock - product.stock_uses
        if difference:
            self.repositories.products.change_stock(product, difference, "Recuento a mano")
        return self.repositories.products.get(product.id)
