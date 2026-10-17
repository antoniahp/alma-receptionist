from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_dashboard.query import GetDashboardQuery
from application.queries.get_dashboard.query_dto import GetDashboardQueryDTO
from infrastructure import dependencies
from infrastructure.api.dashboard.serializer import DashboardSerializer


class DashboardView(APIView):
    def get(self, request):
        return Response(DashboardSerializer(GetDashboardQuery(dependencies.get_repositories()).execute(GetDashboardQueryDTO())).data)
