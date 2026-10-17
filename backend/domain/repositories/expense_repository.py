from abc import ABC, abstractmethod


class ExpenseRepository(ABC):
    @abstractmethod
    def create(self, concept, category, amount, date):
        pass

    @abstractmethod
    def get(self, expense_id):
        """Devuelve el gasto o lanza Expense.DoesNotExist."""

    @abstractmethod
    def delete(self, expense):
        pass

    @abstractmethod
    def list_between(self, start_date, end_date):
        """Gastos con fecha desde start_date (incluida) hasta end_date (sin incluir)."""
