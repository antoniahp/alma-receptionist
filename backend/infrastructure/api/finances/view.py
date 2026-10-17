from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_finances.query import GetFinancesQuery
from application.queries.get_finances.query_dto import GetFinancesQueryDTO
from infrastructure import dependencies
from infrastructure.api.finances.serializer import FinancesQuerySerializer, FinancesSerializer


class FinancesView(APIView):
    def get(self, request):
        params = FinancesQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        month = params.validated_data.get("month") or timezone.localdate()
        finances = GetFinancesQuery(dependencies.get_repositories()).execute(GetFinancesQueryDTO(month=month))
        return Response(FinancesSerializer(finances).data)
