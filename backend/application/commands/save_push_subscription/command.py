class SavePushSubscriptionCommand:
    """La dueña ha pulsado "Activar avisos" en un navegador: a partir de ahora le llegan ahí."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.push_subscriptions.save(endpoint=dto.endpoint, p256dh=dto.p256dh, auth=dto.auth)
