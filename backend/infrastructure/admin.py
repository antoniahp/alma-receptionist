from django.contrib import admin

from domain import models


class ServiceProductInline(admin.TabularInline):
    model = models.ServiceProduct
    extra = 1


@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "duration_minutes", "price", "repeat_every_days", "active"]
    list_filter = ["category", "active"]
    inlines = [ServiceProductInline]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "supplier", "stock_uses", "min_uses", "uses_per_unit"]
    list_filter = ["supplier"]


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "telegram_chat_id", "accepts_reminders"]
    search_fields = ["name", "phone"]


@admin.register(models.Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["start", "client", "service", "status", "source"]
    list_filter = ["status", "source", "service"]
    date_hierarchy = "start"


class PurchaseOrderLineInline(admin.TabularInline):
    model = models.PurchaseOrderLine
    extra = 0


@admin.register(models.PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "supplier", "status", "created_at", "sent_at"]
    inlines = [PurchaseOrderLineInline]


@admin.register(models.HelpRequest)
class HelpRequestAdmin(admin.ModelAdmin):
    list_display = ["created_at", "client", "status"]
    list_filter = ["status"]


admin.site.register(models.Supplier)
admin.site.register(models.OpeningHours)
admin.site.register(models.Notification)
admin.site.register(models.StockMovement)
admin.site.register(models.Conversation)


@admin.register(models.ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ["product", "store", "price", "units"]
    list_filter = ["store"]


@admin.register(models.Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["date", "concept", "category", "amount"]
    list_filter = ["category"]
