from domain.exceptions import PushSubscriptionExpired


class SendOwnerPushCommand:
    """Aviso emergente en todos los navegadores donde la dueña activó los avisos. Devuelve a cuántos llegó."""

    def __init__(self, repositories, push_service):
        self.repositories = repositories
        self.push_service = push_service

    def execute(self, dto):
        if not self.push_service.is_enabled():
            return 0
        sent = 0
        for subscription in self.repositories.push_subscriptions.list():
            try:
                self.push_service.send(subscription, dto.title, dto.body[:180], dto.url)
                sent += 1
            except PushSubscriptionExpired:
                self.repositories.push_subscriptions.delete_by_endpoint(subscription.endpoint)
        return sent
