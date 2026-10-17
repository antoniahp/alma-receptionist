from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_public_info.query import GetPublicInfoQuery
from application.queries.get_public_info.query_dto import GetPublicInfoQueryDTO
from infrastructure import dependencies
from infrastructure.api.public_info.serializer import PublicInfoSerializer


class PublicInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(PublicInfoSerializer(GetPublicInfoQuery(dependencies.get_repositories()).execute(GetPublicInfoQueryDTO())).data)
