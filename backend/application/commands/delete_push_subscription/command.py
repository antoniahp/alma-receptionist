class DeletePushSubscriptionCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        self.repositories.push_subscriptions.delete_by_endpoint(dto.endpoint)
