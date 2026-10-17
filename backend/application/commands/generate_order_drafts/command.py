from django.conf import settings
from django.db import transaction

from application.queries.get_stock_forecast.query import GetStockForecastQuery
from application.queries.get_stock_forecast.query_dto import GetStockForecastQueryDTO
from domain.entities.product_forecast import STATUS_ORDER
from domain.exceptions import LanguageModelUnavailable
from domain.rules import customer_messages
from domain.rules import spanish_format as fmt

EMAIL_SCHEMA = {
    "type": "object",
    "properties": {"subject": {"type": "string"}, "body": {"type": "string"}},
    "required": ["subject", "body"],
}


class GenerateOrderDraftsCommand:
    """Prepara un borrador de pedido por proveedor con lo que hace falta pedir. La dueña lo revisa y lo aprueba."""

    def __init__(self, repositories, language_model_service):
        self.repositories = repositories
        self.language_model_service = language_model_service

    def execute(self, dto):
        forecasts = GetStockForecastQuery(self.repositories).execute(GetStockForecastQueryDTO())
        to_order_by_supplier = {}
        for forecast in forecasts:
            if forecast.status == STATUS_ORDER:
                to_order_by_supplier.setdefault(forecast.product.supplier, []).append(forecast)

        drafts = []
        with transaction.atomic():
            for supplier, supplier_forecasts in to_order_by_supplier.items():
                order = self.repositories.purchase_orders.find_draft_for_supplier(supplier)
                if order is None:
                    order = self.repositories.purchase_orders.create(supplier)
                for forecast in supplier_forecasts:
                    self.repositories.purchase_orders.set_line(
                        order, forecast.product, forecast.suggested_units, forecast.product.unit_price
                    )
                self.write_email(order, supplier_forecasts)
                drafts.append(order)
        return [self.repositories.purchase_orders.get(order.id) for order in drafts]

    def write_email(self, order, forecasts):
        lines = [(line.product, line.units) for line in self.repositories.purchase_orders.lines(order)]
        reasons = []
        for forecast in forecasts:
            if forecast.runs_out_for:
                reasons.append(
                    f"{forecast.product.name}: con las reservas se acaba antes de la cita de {fmt.relative_day(forecast.runs_out_for.start)}"
                )
            else:
                reasons.append(f"{forecast.product.name}: quedará por debajo del mínimo tras las reservas")
        try:
            subject, body = self.write_with_ai(order.supplier, lines, "; ".join(reasons))
            order.written_by_ai = True
        except LanguageModelUnavailable:
            subject, body = customer_messages.order_email(settings.BUSINESS, order.supplier, lines)
            order.written_by_ai = False
        order.email_subject = subject
        order.email_body = body
        self.repositories.purchase_orders.save(order, ["email_subject", "email_body", "written_by_ai"])

    def write_with_ai(self, supplier, lines, reasons):
        business = settings.BUSINESS
        items = "\n".join(
            f"- {units} unidades de {product.name}" + (f" (ref. {product.reference})" if product.reference else "")
            for product, units in lines
        )
        contact = f" (contacto: {supplier.contact_name})" if supplier.contact_name else ""
        prompt = (
            f"Escribe un correo breve y cordial en español de España de parte de {business['owner']}, dueña del centro de estética "
            f"{business['name']}, a su proveedor {supplier.name}{contact}. Hace un pedido con exactamente estas líneas, "
            f"sin cambiar cantidades ni añadir productos:\n{items}\n\nContexto para el tono (no lo copies literal): {reasons}\n"
            f"Pide que confirmen precio y plazo de entrega. Firma con el nombre y el teléfono {business['phone']}. "
            "Sin marcadores tipo [Nombre]. Máximo 120 palabras."
        )
        data = self.language_model_service.write_json([{"role": "user", "content": prompt}], EMAIL_SCHEMA, temperature=0.4)
        subject = (data.get("subject") or "").strip()[:200]
        body = (data.get("body") or "").strip()
        # Comprobación: todas las cantidades y productos tienen que aparecer en el correo
        for product, units in lines:
            if str(units) not in body or product.name.split(" ")[0].lower() not in body.lower():
                raise LanguageModelUnavailable("El correo generado no incluye todas las líneas")
        if not subject:
            raise LanguageModelUnavailable("El correo generado no tiene asunto")
        return subject, body
