from domain.entities import PushSubscription
from domain.repositories.push_subscription_repository import PushSubscriptionRepository


class DjangoPushSubscriptionRepository(PushSubscriptionRepository):
    def save(self, endpoint, p256dh, auth):
        subscription, _ = PushSubscription.objects.update_or_create(endpoint=endpoint, defaults={"p256dh": p256dh, "auth": auth})
        return subscription

    def list(self):
        return list(PushSubscription.objects.all())

    def delete_by_endpoint(self, endpoint):
        PushSubscription.objects.filter(endpoint=endpoint).delete()
