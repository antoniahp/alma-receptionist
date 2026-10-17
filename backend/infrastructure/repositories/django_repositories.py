from domain.repositories.repositories import Repositories
from infrastructure.repositories.django_appointment_repository import DjangoAppointmentRepository
from infrastructure.repositories.django_cash_closing_repository import DjangoCashClosingRepository
from infrastructure.repositories.django_client_repository import DjangoClientRepository
from infrastructure.repositories.django_conversation_repository import DjangoConversationRepository
from infrastructure.repositories.django_expense_repository import DjangoExpenseRepository
from infrastructure.repositories.django_help_request_repository import DjangoHelpRequestRepository
from infrastructure.repositories.django_notification_repository import DjangoNotificationRepository
from infrastructure.repositories.django_opening_hours_repository import DjangoOpeningHoursRepository
from infrastructure.repositories.django_pack_repository import DjangoPackRepository
from infrastructure.repositories.django_product_repository import DjangoProductRepository
from infrastructure.repositories.django_purchase_order_repository import DjangoPurchaseOrderRepository
from infrastructure.repositories.django_push_subscription_repository import DjangoPushSubscriptionRepository
from infrastructure.repositories.django_service_repository import DjangoServiceRepository
from infrastructure.repositories.django_shopping_list_repository import DjangoShoppingListRepository
from infrastructure.repositories.django_supplier_repository import DjangoSupplierRepository
from infrastructure.repositories.django_time_block_repository import DjangoTimeBlockRepository


def build_django_repositories():
    return Repositories(
        appointments=DjangoAppointmentRepository(),
        clients=DjangoClientRepository(),
        services=DjangoServiceRepository(),
        products=DjangoProductRepository(),
        opening_hours=DjangoOpeningHoursRepository(),
        purchase_orders=DjangoPurchaseOrderRepository(),
        notifications=DjangoNotificationRepository(),
        conversations=DjangoConversationRepository(),
        help_requests=DjangoHelpRequestRepository(),
        suppliers=DjangoSupplierRepository(),
        shopping_list=DjangoShoppingListRepository(),
        expenses=DjangoExpenseRepository(),
        packs=DjangoPackRepository(),
        time_blocks=DjangoTimeBlockRepository(),
        push_subscriptions=DjangoPushSubscriptionRepository(),
        cash_closings=DjangoCashClosingRepository(),
    )
