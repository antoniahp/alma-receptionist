from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.add_expense.command import AddExpenseCommand
from application.commands.add_expense.command_dto import AddExpenseCommandDTO
from infrastructure import dependencies
from infrastructure.api.expenses.serializer import AddExpenseSerializer
from infrastructure.api.finances.serializer import ExpenseSerializer


class ExpenseListView(APIView):
    def post(self, request):
        serializer = AddExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expense = AddExpenseCommand(dependencies.get_repositories()).execute(AddExpenseCommandDTO(**serializer.validated_data))
        return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)
