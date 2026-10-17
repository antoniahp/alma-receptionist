"""Entidades del dominio: los modelos que se guardan en la base de datos y los objetos de valor que no."""

from domain.entities.appointment import Appointment
from domain.entities.cash_closing import CashClosing
from domain.entities.client import Client
from domain.entities.client_pack import ClientPack
from domain.entities.conversation import ChatMessage, Conversation
from domain.entities.expense import Expense
from domain.entities.help_request import HelpRequest
from domain.entities.notification import Notification
from domain.entities.opening_hours import OpeningHours
from domain.entities.product import Product
from domain.entities.purchase_order import PurchaseOrder, PurchaseOrderLine
from domain.entities.push_subscription import PushSubscription
from domain.entities.service import Service, ServiceProduct
from domain.entities.shopping_list_item import ShoppingListItem
from domain.entities.stock_movement import StockMovement
from domain.entities.supplier import Supplier
from domain.entities.time_block import TimeBlock

__all__ = [
    "Appointment",
    "CashClosing",
    "ChatMessage",
    "Client",
    "ClientPack",
    "Conversation",
    "Expense",
    "HelpRequest",
    "Notification",
    "OpeningHours",
    "Product",
    "PurchaseOrder",
    "PushSubscription",
    "PurchaseOrderLine",
    "Service",
    "ServiceProduct",
    "ShoppingListItem",
    "StockMovement",
    "Supplier",
    "TimeBlock",
]
