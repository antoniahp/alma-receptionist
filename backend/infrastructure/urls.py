"""Todas las rutas de la API en un solo sitio."""

from django.urls import path

from infrastructure.api.appointment_actions.view import (
    CancelAppointmentView,
    CompleteAppointmentView,
    NoShowAppointmentView,
    RemindAppointmentView,
    UndoCompleteAppointmentView,
)
from infrastructure.api.appointments.view import AppointmentListView
from infrastructure.api.auth_login.view import LoginView
from infrastructure.api.cash_day.view import CashDayView
from infrastructure.api.client_detail.view import ClientDetailView
from infrastructure.api.client_forget.view import ForgetClientView
from infrastructure.api.clients.view import ClientListView
from infrastructure.api.conversations.view import ConversationListView
from infrastructure.api.current_user.view import CurrentUserView
from infrastructure.api.dashboard.view import DashboardView
from infrastructure.api.expense_detail.view import ExpenseDetailView
from infrastructure.api.expenses.view import ExpenseListView
from infrastructure.api.finances.view import FinancesView
from infrastructure.api.finances_export.view import FinancesExportView
from infrastructure.api.help_request_actions.view import AnswerHelpRequestView, CloseHelpRequestView
from infrastructure.api.help_requests.view import HelpRequestListView
from infrastructure.api.notification_actions.view import SendDueNotificationsView, SendReactivationView
from infrastructure.api.notifications.view import NotificationListView
from infrastructure.api.packs.view import PackListView
from infrastructure.api.pending_notifications.view import PendingNotificationsView
from infrastructure.api.product_count.view import ProductCountView
from infrastructure.api.product_prices.view import ProductPricesView
from infrastructure.api.products.view import ProductListView
from infrastructure.api.public_availability.view import PublicAvailabilityView
from infrastructure.api.public_booking.view import PublicBookingView
from infrastructure.api.public_chat.view import PublicChatView
from infrastructure.api.public_chat_updates.view import PublicChatUpdatesView
from infrastructure.api.public_info.view import PublicInfoView
from infrastructure.api.purchase_order_actions.view import ApproveOrderView, DiscardOrderView, GenerateOrderDraftsView, ReceiveOrderView
from infrastructure.api.purchase_orders.view import PurchaseOrderDetailView, PurchaseOrderListView
from infrastructure.api.push_subscriptions.view import PushSubscriptionView
from infrastructure.api.service_detail.view import ServiceDetailView
from infrastructure.api.services.view import ServiceListView
from infrastructure.api.shopping_list.view import ShoppingListView
from infrastructure.api.shopping_list_item.view import ShoppingListItemView
from infrastructure.api.shopping_list_order.view import OrderFromStoreView
from infrastructure.api.stock_forecast.view import StockForecastView
from infrastructure.api.store_link.view import StoreLinkView
from infrastructure.api.supplier_detail.view import SupplierDetailView
from infrastructure.api.suppliers.view import SupplierListView
from infrastructure.api.system_status.view import SystemStatusView
from infrastructure.api.time_block_detail.view import TimeBlockDetailView
from infrastructure.api.time_blocks.view import TimeBlockListView

urlpatterns = [
    path("auth/login/", LoginView.as_view()),
    path("auth/me/", CurrentUserView.as_view()),
    path("status/", SystemStatusView.as_view()),
    path("dashboard/", DashboardView.as_view()),
    path("finances/", FinancesView.as_view()),
    path("finances/export/", FinancesExportView.as_view()),
    path("expenses/", ExpenseListView.as_view()),
    path("expenses/<uuid:expense_id>/", ExpenseDetailView.as_view()),
    path("services/", ServiceListView.as_view()),
    path("services/<uuid:service_id>/", ServiceDetailView.as_view()),
    path("clients/", ClientListView.as_view()),
    path("clients/<uuid:client_id>/", ClientDetailView.as_view()),
    path("clients/<uuid:client_id>/forget/", ForgetClientView.as_view()),
    path("appointments/", AppointmentListView.as_view()),
    path("appointments/<uuid:appointment_id>/complete/", CompleteAppointmentView.as_view()),
    path("appointments/<uuid:appointment_id>/undo-complete/", UndoCompleteAppointmentView.as_view()),
    path("packs/", PackListView.as_view()),
    path("cash/", CashDayView.as_view()),
    path("blocks/", TimeBlockListView.as_view()),
    path("blocks/<uuid:block_id>/", TimeBlockDetailView.as_view()),
    path("appointments/<uuid:appointment_id>/cancel/", CancelAppointmentView.as_view()),
    path("appointments/<uuid:appointment_id>/no-show/", NoShowAppointmentView.as_view()),
    path("appointments/<uuid:appointment_id>/remind/", RemindAppointmentView.as_view()),
    path("products/", ProductListView.as_view()),
    path("products/forecast/", StockForecastView.as_view()),
    path("products/<uuid:product_id>/count/", ProductCountView.as_view()),
    path("products/<uuid:product_id>/prices/", ProductPricesView.as_view()),
    path("offers/store-link/", StoreLinkView.as_view()),
    path("shopping-list/", ShoppingListView.as_view()),
    path("shopping-list/order/", OrderFromStoreView.as_view()),
    path("shopping-list/<uuid:item_id>/", ShoppingListItemView.as_view()),
    path("orders/", PurchaseOrderListView.as_view()),
    path("orders/<uuid:order_id>/", PurchaseOrderDetailView.as_view()),
    path("orders/generate/", GenerateOrderDraftsView.as_view()),
    path("orders/<uuid:order_id>/approve/", ApproveOrderView.as_view()),
    path("orders/<uuid:order_id>/receive/", ReceiveOrderView.as_view()),
    path("orders/<uuid:order_id>/discard/", DiscardOrderView.as_view()),
    path("suppliers/", SupplierListView.as_view()),
    path("suppliers/<uuid:supplier_id>/", SupplierDetailView.as_view()),
    path("notifications/", NotificationListView.as_view()),
    path("push/", PushSubscriptionView.as_view()),
    path("notifications/pending/", PendingNotificationsView.as_view()),
    path("notifications/run/", SendDueNotificationsView.as_view()),
    path("notifications/reactivate/", SendReactivationView.as_view()),
    path("conversations/", ConversationListView.as_view()),
    path("help-requests/", HelpRequestListView.as_view()),
    path("help-requests/<uuid:help_request_id>/reply/", AnswerHelpRequestView.as_view()),
    path("help-requests/<uuid:help_request_id>/close/", CloseHelpRequestView.as_view()),
    path("public/info/", PublicInfoView.as_view()),
    path("public/availability/", PublicAvailabilityView.as_view()),
    path("public/book/", PublicBookingView.as_view()),
    path("public/chat/", PublicChatView.as_view()),
    path("public/chat/updates/", PublicChatUpdatesView.as_view()),
]
