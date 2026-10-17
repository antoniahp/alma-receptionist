from domain.entities import Notification
from domain.repositories.notification_repository import NotificationRepository


class DjangoNotificationRepository(NotificationRepository):
    def create(self, kind, text, status, client_id=None, error="", appointment_id=None, service_id=None, telegram_message_id=""):
        return Notification.objects.create(
            kind=kind,
            text=text,
            status=status,
            client_id=client_id,
            error=error,
            appointment_id=appointment_id,
            service_id=service_id,
            telegram_message_id=telegram_message_id,
        )

    def list_recent(self, limit):
        return list(Notification.objects.select_related("client")[:limit])

    def reactivation_sent_since(self, client_id, service_id, since):
        notifications = Notification.objects.filter(
            client_id=client_id, service_id=service_id, kind=Notification.REACTIVATION, created_at__gt=since
        )
        return notifications.exists()
