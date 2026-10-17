from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.count_stock.command import CountStockCommand
from application.commands.count_stock.command_dto import CountStockCommandDTO
from infrastructure import dependencies
from infrastructure.api.product_count.serializer import CountStockSerializer
from infrastructure.api.products.serializer import ProductSerializer


class ProductCountView(APIView):
    def post(self, request, product_id):
        serializer = CountStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = CountStockCommand(dependencies.get_repositories()).execute(
            CountStockCommandDTO(product_id=product_id, uses_in_stock=serializer.validated_data["uses_in_stock"])
        )
        return Response(ProductSerializer(product).data)
