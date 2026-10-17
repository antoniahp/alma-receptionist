from datetime import timedelta

from django.utils import timezone

from domain.rules.stock_forecast_calculator import calculate_product_forecast


class GetStockForecastQuery:
    """Previsión de cada producto cruzando el stock con lo que gastarán las citas reservadas."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        # Incluye las citas de las últimas 3 horas que aún no se han marcado como completadas
        upcoming = self.repositories.appointments.list_active_since(timezone.now() - timedelta(hours=3))
        products_in_open_orders = self.repositories.purchase_orders.product_ids_in_open_orders()
        forecasts = []
        for product in self.repositories.products.list_with_supplier():
            upcoming_uses = []
            for appointment in upcoming:
                uses = sum(item.uses for item in appointment.service.consumption.all() if item.product_id == product.id)
                if uses:
                    upcoming_uses.append((appointment, uses))
            forecasts.append(calculate_product_forecast(product, upcoming_uses, product.id in products_in_open_orders))
        return forecasts
