class ListPurchaseOrdersQuery:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        return self.repositories.purchase_orders.list(dto.statuses)
