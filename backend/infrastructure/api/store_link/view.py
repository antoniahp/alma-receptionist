from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_store_link.query import GetStoreLinkQuery
from application.queries.get_store_link.query_dto import GetStoreLinkQueryDTO
from infrastructure import dependencies
from infrastructure.api.store_link.serializer import StoreLinkSerializer


class StoreLinkView(APIView):
    def get(self, request):
        serializer = StoreLinkSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        link = GetStoreLinkQuery(dependencies.get_price_search_service(), dependencies.get_repositories()).execute(
            GetStoreLinkQueryDTO(page_token=serializer.validated_data["token"], store=serializer.validated_data["store"])
        )
        return Response({"link": link})
