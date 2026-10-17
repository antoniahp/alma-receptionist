from django.utils import timezone

from application.queries.get_finances.query import month_bounds
from domain.entities import Appointment, Expense, payment
from domain.rules import months

INCOME = "Ingreso"
SPENDING = "Gasto"


class ExportFinancesQuery:
    """Movimientos de un mes en filas, para pasárselos a la gestoría."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        month = months.first_day(dto.month)
        start, end = month_bounds(month)
        methods = dict(payment.METHODS)
        expense_labels = dict(Expense.CATEGORIES)
        rows = []

        for appointment in self.repositories.appointments.list_between(start, end, [Appointment.COMPLETED]):
            method = appointment.payment_method or payment.CASH
            rows.append(
                {
                    "date": timezone.localtime(appointment.start).date(),
                    "type": INCOME,
                    "concept": appointment.service.name,
                    "category": appointment.service.get_category_display(),
                    "payment_method": methods[method],
                    "amount": appointment.cashed_amount,
                }
            )
        for pack in self.repositories.packs.list_sold_between(start, end):
            rows.append(
                {
                    "date": timezone.localtime(pack.sold_at).date(),
                    "type": INCOME,
                    "concept": f"Bono {pack.sessions_total} × {pack.service.name}",
                    "category": "Bonos",
                    "payment_method": methods[pack.payment_method],
                    "amount": pack.price,
                }
            )
        for order in self.repositories.purchase_orders.list_ordered_between(start, end):
            rows.append(
                {
                    "date": timezone.localtime(order.sent_at).date(),
                    "type": SPENDING,
                    "concept": f"Pedido a {order.supplier.name}",
                    "category": "Productos",
                    "payment_method": "",
                    "amount": order.total,
                }
            )
        for expense in self.repositories.expenses.list_between(month, months.next_month(month)):
            rows.append(
                {
                    "date": expense.date,
                    "type": SPENDING,
                    "concept": expense.concept,
                    "category": expense_labels.get(expense.category, "Otros"),
                    "payment_method": "",
                    "amount": expense.amount,
                }
            )
        return sorted(rows, key=lambda row: (row["date"], row["type"]))
