from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.delete_expense.command import DeleteExpenseCommand
from application.commands.delete_expense.command_dto import DeleteExpenseCommandDTO
from infrastructure import dependencies


class ExpenseDetailView(APIView):
    def delete(self, request, expense_id):
        DeleteExpenseCommand(dependencies.get_repositories()).execute(DeleteExpenseCommandDTO(expense_id=expense_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
