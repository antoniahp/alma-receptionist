from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_stock_forecast.query import GetStockForecastQuery
from application.queries.get_stock_forecast.query_dto import GetStockForecastQueryDTO
from infrastructure import dependencies
from infrastructure.api.stock_forecast.serializer import StockForecastSerializer


class StockForecastView(APIView):
    def get(self, request):
        forecasts = GetStockForecastQuery(dependencies.get_repositories()).execute(GetStockForecastQueryDTO())
        return Response(StockForecastSerializer(forecasts, many=True).data)
