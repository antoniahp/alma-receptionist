from domain.entities import Expense
from domain.exceptions import InvalidExpense


class AddExpenseCommand:
    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        concept = dto.concept.strip()
        if not concept or dto.amount <= 0:
            raise InvalidExpense()
        category = dto.category if dto.category in dict(Expense.CATEGORIES) else Expense.OTHER
        return self.repositories.expenses.create(concept=concept[:120], category=category, amount=dto.amount, date=dto.date)
