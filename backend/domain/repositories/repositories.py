from dataclasses import dataclass

from domain.repositories.appointment_repository import AppointmentRepository
from domain.repositories.cash_closing_repository import CashClosingRepository
from domain.repositories.client_repository import ClientRepository
from domain.repositories.conversation_repository import ConversationRepository
from domain.repositories.expense_repository import ExpenseRepository
from domain.repositories.help_request_repository import HelpRequestRepository
from domain.repositories.notification_repository import NotificationRepository
from domain.repositories.opening_hours_repository import OpeningHoursRepository
from domain.repositories.pack_repository import PackRepository
from domain.repositories.product_repository import ProductRepository
from domain.repositories.purchase_order_repository import PurchaseOrderRepository
from domain.repositories.push_subscription_repository import PushSubscriptionRepository
from domain.repositories.service_repository import ServiceRepository
from domain.repositories.shopping_list_repository import ShoppingListRepository
from domain.repositories.supplier_repository import SupplierRepository
from domain.repositories.time_block_repository import TimeBlockRepository


@dataclass(frozen=True)
class Repositories:
    """Todos los repositorios juntos, para pasarlos a los commands y queries con un solo parámetro."""

    appointments: AppointmentRepository
    clients: ClientRepository
    services: ServiceRepository
    products: ProductRepository
    opening_hours: OpeningHoursRepository
    purchase_orders: PurchaseOrderRepository
    notifications: NotificationRepository
    conversations: ConversationRepository
    help_requests: HelpRequestRepository
    suppliers: SupplierRepository
    shopping_list: ShoppingListRepository
    expenses: ExpenseRepository
    packs: PackRepository
    time_blocks: TimeBlockRepository
    push_subscriptions: PushSubscriptionRepository
    cash_closings: CashClosingRepository
