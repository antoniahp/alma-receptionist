from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from application.queries.get_stock_forecast.query import GetStockForecastQuery
from application.queries.get_stock_forecast.query_dto import GetStockForecastQueryDTO
from application.queries.list_due_reactivations.query import ListDueReactivationsQuery
from application.queries.list_due_reactivations.query_dto import ListDueReactivationsQueryDTO
from application.queries.list_due_reminders.query import ListDueRemindersQuery
from application.queries.list_due_reminders.query_dto import ListDueRemindersQueryDTO
from application.shared.schedule import start_of_day
from domain.entities import Appointment
from domain.entities.product_forecast import STATUS_ORDER


class GetDashboardQuery:
    """Resumen para la portada del panel."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        day_start = start_of_day(timezone.localdate())
        statuses = list(Appointment.ACTIVE_STATUSES) + [Appointment.COMPLETED]
        todays_appointments = self.repositories.appointments.list_between(day_start, day_start + timedelta(days=1), statuses)

        revenue = Decimal("0")
        for appointment in todays_appointments:
            # Las completadas, lo cobrado de verdad; las pendientes, su precio
            revenue += appointment.cashed_amount if appointment.status == Appointment.COMPLETED else appointment.charged_price

        forecasts = GetStockForecastQuery(self.repositories).execute(GetStockForecastQueryDTO())
        return {
            "appointments_today": len(todays_appointments),
            "revenue_today": revenue,
            # Solo cuenta lo que se puede enviar: a quien no tiene Telegram no le llega nada
            "reminders_due": len(
                [a for a in ListDueRemindersQuery(self.repositories).execute(ListDueRemindersQueryDTO()) if a.client.has_telegram]
            ),
            "reactivations_due": len(
                [c for c in ListDueReactivationsQuery(self.repositories).execute(ListDueReactivationsQueryDTO()) if c.client.has_telegram]
            ),
            "products_to_order": len([forecast for forecast in forecasts if forecast.status == STATUS_ORDER]),
            "orders_to_approve": self.repositories.purchase_orders.count_drafts(),
            "help_requests_open": self.repositories.help_requests.count_open(),
            # Para avisar a la dueña si tiene el panel abierto: la última pregunta que le ha pasado Aura
            "latest_help_request": self.repositories.help_requests.last_open(),
        }
