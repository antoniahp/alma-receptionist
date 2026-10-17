from decimal import Decimal

from rest_framework import serializers

from domain.entities import Expense


class AddExpenseSerializer(serializers.Serializer):
    concept = serializers.CharField(max_length=120)
    category = serializers.ChoiceField(choices=Expense.CATEGORIES, required=False, default=Expense.OTHER)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    date = serializers.DateField()
