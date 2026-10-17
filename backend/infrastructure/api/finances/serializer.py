from rest_framework import serializers

MONEY = {"max_digits": 12, "decimal_places": 2}


class FinancesQuerySerializer(serializers.Serializer):
    month = serializers.DateField(input_formats=["%Y-%m"], required=False)


class ExpenseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    concept = serializers.CharField()
    category = serializers.CharField()
    category_label = serializers.CharField(source="get_category_display")
    amount = serializers.DecimalField(**MONEY)
    date = serializers.DateField()


class OrderSpendingSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    supplier = serializers.CharField(source="supplier.name")
    sent_at = serializers.DateTimeField()
    total = serializers.DecimalField(**MONEY)


class IncomeCategorySerializer(serializers.Serializer):
    label = serializers.CharField()
    amount = serializers.DecimalField(**MONEY)
    count = serializers.IntegerField()


class SpendingCategorySerializer(serializers.Serializer):
    label = serializers.CharField()
    amount = serializers.DecimalField(**MONEY)


class MonthSummarySerializer(serializers.Serializer):
    month = serializers.DateField()
    income = serializers.DecimalField(**MONEY)
    spending = serializers.DecimalField(**MONEY)
    profit = serializers.DecimalField(**MONEY)


class FinancesSerializer(serializers.Serializer):
    month = serializers.DateField()
    income = serializers.DecimalField(**MONEY)
    appointments_completed = serializers.IntegerField()
    expected_income = serializers.DecimalField(**MONEY)
    income_by_category = IncomeCategorySerializer(many=True)
    spending = serializers.DecimalField(**MONEY)
    product_spending = serializers.DecimalField(**MONEY)
    orders = OrderSpendingSerializer(many=True)
    other_spending = serializers.DecimalField(**MONEY)
    spending_by_category = SpendingCategorySerializer(many=True)
    expenses = ExpenseSerializer(many=True)
    profit = serializers.DecimalField(**MONEY)
    history = MonthSummarySerializer(many=True)
