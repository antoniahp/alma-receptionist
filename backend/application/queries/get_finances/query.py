from datetime import datetime, time
from decimal import Decimal

from django.utils import timezone

from domain.entities import Appointment, Expense
from domain.rules import months


def month_bounds(month):
    """Inicio y fin del mes como fecha y hora del centro."""
    start = timezone.make_aware(datetime.combine(month, time.min))
    end = timezone.make_aware(datetime.combine(months.next_month(month), time.min))
    return start, end


class GetFinancesQuery:
    """Ingresos (citas completadas), gastos (pedidos de producto + gastos apuntados) y beneficio de un mes."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        month = months.first_day(dto.month)
        start, end = month_bounds(month)

        completed = self.repositories.appointments.list_between(start, end, [Appointment.COMPLETED])
        orders = self.repositories.purchase_orders.list_ordered_between(start, end)
        expenses = self.repositories.expenses.list_between(month, months.next_month(month))

        packs = self.repositories.packs.list_sold_between(start, end)
        # Lo que entra en caja: las citas (las pagadas con bono no, porque el bono se cobró al venderlo) y los bonos vendidos
        income = sum((appointment.cashed_amount for appointment in completed), Decimal("0")) + sum(
            (pack.price for pack in packs), Decimal("0")
        )
        product_spending = sum((order.total for order in orders), Decimal("0"))
        other_spending = sum((expense.amount for expense in expenses), Decimal("0"))
        spending = product_spending + other_spending

        return {
            "month": month,
            "income": income,
            "appointments_completed": len(completed),
            "expected_income": self.expected_income(start, end),
            "income_by_category": self.income_by_category(completed, packs),
            "spending": spending,
            "product_spending": product_spending,
            "orders": orders,
            "other_spending": other_spending,
            "spending_by_category": self.spending_by_category(expenses),
            "expenses": expenses,
            "profit": income - spending,
            "history": self.history(month, dto.months_of_history),
        }

    def expected_income(self, start, end):
        """Lo que falta por cobrar este mes: citas reservadas desde ahora hasta fin de mes."""
        now = timezone.now()
        if end <= now:
            return Decimal("0")
        upcoming = self.repositories.appointments.list_between(max(start, now), end, list(Appointment.ACTIVE_STATUSES))
        # Las que se pagarán con un bono no traen dinero nuevo
        with_pack = self.repositories.packs.active_pairs({appointment.client_id for appointment in upcoming})
        return sum(
            (a.charged_price for a in upcoming if (a.client_id, a.service_id) not in with_pack),
            Decimal("0"),
        )

    def income_by_category(self, completed, packs):
        totals = {}
        for appointment in completed:
            label = appointment.service.get_category_display()
            if label not in totals:
                totals[label] = {"label": label, "amount": Decimal("0"), "count": 0}
            totals[label]["amount"] += appointment.cashed_amount
            totals[label]["count"] += 1
        for pack in packs:
            if "Bonos" not in totals:
                totals["Bonos"] = {"label": "Bonos", "amount": Decimal("0"), "count": 0}
            totals["Bonos"]["amount"] += pack.price
            totals["Bonos"]["count"] += 1
        return sorted(totals.values(), key=lambda item: item["amount"], reverse=True)

    def spending_by_category(self, expenses):
        labels = dict(Expense.CATEGORIES)
        totals = {}
        for expense in expenses:
            label = labels.get(expense.category, "Otros")
            totals[label] = totals.get(label, Decimal("0")) + expense.amount
        return sorted(
            ({"label": label, "amount": amount} for label, amount in totals.items()), key=lambda item: item["amount"], reverse=True
        )

    def history(self, month, how_many):
        """Ingresos y gastos de los últimos meses (el más antiguo primero), para la gráfica."""
        result = []
        current = month
        for _ in range(how_many):
            start, end = month_bounds(current)
            completed = self.repositories.appointments.list_between(start, end, [Appointment.COMPLETED])
            orders = self.repositories.purchase_orders.list_ordered_between(start, end)
            expenses = self.repositories.expenses.list_between(current, months.next_month(current))
            packs = self.repositories.packs.list_sold_between(start, end)
            income = sum((appointment.cashed_amount for appointment in completed), Decimal("0")) + sum(
                (pack.price for pack in packs), Decimal("0")
            )
            spending = sum((order.total for order in orders), Decimal("0")) + sum((expense.amount for expense in expenses), Decimal("0"))
            result.append({"month": current, "income": income, "spending": spending, "profit": income - spending})
            current = months.previous_month(current)
        return list(reversed(result))
