from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.add_to_shopping_list.command import AddToShoppingListCommand
from application.commands.add_to_shopping_list.command_dto import AddToShoppingListCommandDTO
from application.queries.get_shopping_list.query import GetShoppingListQuery
from application.queries.get_shopping_list.query_dto import GetShoppingListQueryDTO
from infrastructure import dependencies
from infrastructure.api.shared.serializers import ShoppingListGroupSerializer, ShoppingListItemSerializer
from infrastructure.api.shopping_list.serializer import AddToShoppingListSerializer


class ShoppingListView(APIView):
    def get(self, request):
        groups = GetShoppingListQuery(dependencies.get_repositories()).execute(GetShoppingListQueryDTO())
        return Response(ShoppingListGroupSerializer(groups, many=True).data)

    def post(self, request):
        serializer = AddToShoppingListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        item = AddToShoppingListCommand(dependencies.get_repositories(), dependencies.get_price_search_service()).execute(
            AddToShoppingListCommandDTO(
                product_id=data["product"],
                store=data["store"],
                title=data["title"],
                price=data["price"],
                link=data["link"],
                units=data["units"],
                page_token=data["page_token"],
            )
        )
        return Response(ShoppingListItemSerializer(item).data, status=status.HTTP_201_CREATED)
