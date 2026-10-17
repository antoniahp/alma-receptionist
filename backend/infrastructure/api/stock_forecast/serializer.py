from rest_framework import serializers

from domain.rules import spanish_format as fmt


class StockForecastSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="product.id")
    name = serializers.CharField(source="product.name")
    reference = serializers.CharField(source="product.reference")
    supplier = serializers.UUIDField(source="product.supplier_id")
    supplier_name = serializers.CharField(source="product.supplier.name")
    unit_price = serializers.DecimalField(source="product.unit_price", max_digits=8, decimal_places=2)
    uses_per_unit = serializers.IntegerField(source="product.uses_per_unit")
    stock_uses = serializers.IntegerField(source="stock")
    min_uses = serializers.IntegerField(source="product.min_uses")
    reserved = serializers.IntegerField()
    after_bookings = serializers.IntegerField()
    status = serializers.CharField()
    suggested_units = serializers.IntegerField()
    runs_out_for = serializers.SerializerMethodField()

    def get_runs_out_for(self, forecast):
        appointment = forecast.runs_out_for
        if appointment is None:
            return None
        return {"client": appointment.client.first_name, "start": appointment.start, "when": fmt.when(appointment.start)}
