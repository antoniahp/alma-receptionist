class DeleteExpenseCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        expense = self.repositories.expenses.get(dto.expense_id)
        self.repositories.expenses.delete(expense)
