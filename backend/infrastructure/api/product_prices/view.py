from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.compare_product_prices.query import CompareProductPricesQuery
from application.queries.compare_product_prices.query_dto import CompareProductPricesQueryDTO
from infrastructure import dependencies
from infrastructure.api.product_prices.serializer import PriceComparisonSerializer


class ProductPricesView(APIView):
    def get(self, request, product_id):
        comparison = CompareProductPricesQuery(dependencies.get_repositories(), dependencies.get_price_search_service()).execute(
            CompareProductPricesQueryDTO(product_id=product_id)
        )
        return Response(PriceComparisonSerializer(comparison).data)
