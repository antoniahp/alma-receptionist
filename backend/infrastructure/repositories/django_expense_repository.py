from domain.entities import Expense
from domain.repositories.expense_repository import ExpenseRepository


class DjangoExpenseRepository(ExpenseRepository):
    def create(self, concept, category, amount, date):
        return Expense.objects.create(concept=concept, category=category, amount=amount, date=date)

    def get(self, expense_id):
        return Expense.objects.get(pk=expense_id)

    def delete(self, expense):
        expense.delete()

    def list_between(self, start_date, end_date):
        return list(Expense.objects.filter(date__gte=start_date, date__lt=end_date))
