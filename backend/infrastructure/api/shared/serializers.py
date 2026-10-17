"""Serializadores que se reutilizan en varias vistas."""

from rest_framework import serializers

from infrastructure.api.shared.localized import localized
from infrastructure.services.telegram_message_service import telegram_deep_link


class ChatButtonSerializer(serializers.Serializer):
    label = serializers.CharField()
    data = serializers.CharField()


class ChatReplySerializer(serializers.Serializer):
    text = serializers.CharField()
    buttons = serializers.ListField(child=ChatButtonSerializer(many=True))
    by_ai = serializers.BooleanField()
    appointment_id = serializers.UUIDField(allow_null=True)


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.CharField()
    text = serializers.CharField()
    by_ai = serializers.BooleanField()
    from_owner = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class SupplierSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    contact_name = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()


class ClientSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()
    notes = serializers.CharField()
    accepts_reminders = serializers.BooleanField()
    has_telegram = serializers.BooleanField()
    telegram_link = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    # Solo vienen en el listado de clientas (los calcula el repositorio)
    visits_count = serializers.IntegerField(required=False, default=0)
    last_visit = serializers.DateTimeField(required=False, allow_null=True, default=None)
    next_visit = serializers.DateTimeField(required=False, allow_null=True, default=None)

    def get_telegram_link(self, client):
        return telegram_deep_link(client)


class AppointmentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    client = serializers.UUIDField(source="client_id")
    client_name = serializers.CharField(source="client.name")
    client_has_telegram = serializers.BooleanField(source="client.has_telegram")
    client_telegram_link = serializers.SerializerMethodField()
    service = serializers.UUIDField(source="service_id")
    service_name = serializers.SerializerMethodField()
    duration_minutes = serializers.IntegerField(source="service.duration_minutes")
    price = serializers.DecimalField(source="charged_price", max_digits=8, decimal_places=2)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    status = serializers.CharField()
    source = serializers.CharField()
    notes = serializers.CharField()
    reminder_sent_at = serializers.DateTimeField(allow_null=True)
    payment_method = serializers.CharField()
    completed_at = serializers.DateTimeField(allow_null=True)
    # Lo calcula la vista (context "pack_pairs"): la clienta tiene un bono con sesiones para este servicio
    client_has_pack = serializers.SerializerMethodField()
    consumption = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_service_name(self, appointment):
        return localized(appointment.service, "name")

    def get_client_has_pack(self, appointment):
        return (appointment.client_id, appointment.service_id) in self.context.get("pack_pairs", set())

    def get_client_telegram_link(self, appointment):
        return telegram_deep_link(appointment.client)

    def get_consumption(self, appointment):
        return [{"product": item.product.name, "uses": item.uses} for item in appointment.service.consumption.all()]


class NotificationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    client = serializers.UUIDField(source="client_id", allow_null=True)
    client_name = serializers.SerializerMethodField()
    kind = serializers.CharField()
    text = serializers.CharField()
    status = serializers.CharField()
    error = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_client_name(self, notification):
        return notification.client.name if notification.client else ""


class PurchaseOrderLineSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product = serializers.UUIDField(source="product_id")
    product_name = serializers.CharField(source="product.name")
    units = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=8, decimal_places=2)
    uses_added = serializers.IntegerField()


class PurchaseOrderSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    supplier = SupplierSerializer()
    status = serializers.CharField()
    email_subject = serializers.CharField()
    email_body = serializers.CharField()
    written_by_ai = serializers.BooleanField()
    lines = PurchaseOrderLineSerializer(many=True, source="lines.all")
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()
    sent_at = serializers.DateTimeField(allow_null=True)
    received_at = serializers.DateTimeField(allow_null=True)


class ShoppingListItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    product = serializers.UUIDField(source="product_id")
    product_name = serializers.CharField(source="product.name")
    store = serializers.CharField()
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    link = serializers.CharField()
    units = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class ShoppingListGroupSerializer(serializers.Serializer):
    store = serializers.CharField()
    is_supplier = serializers.SerializerMethodField()
    supplier_email = serializers.SerializerMethodField()
    items = ShoppingListItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    cart_link = serializers.CharField()
    trusted = serializers.BooleanField()

    def get_is_supplier(self, group):
        return group["supplier"] is not None

    def get_supplier_email(self, group):
        return group["supplier"].email if group["supplier"] else ""


class PackSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    service = serializers.UUIDField(source="service_id")
    service_name = serializers.SerializerMethodField()
    sessions_total = serializers.IntegerField()
    sessions_used = serializers.IntegerField()
    sessions_left = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    payment_method = serializers.CharField()
    sold_at = serializers.DateTimeField()

    def get_service_name(self, pack):
        return localized(pack.service, "name")
