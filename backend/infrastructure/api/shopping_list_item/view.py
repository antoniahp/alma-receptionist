from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.change_shopping_list_units.command import ChangeShoppingListUnitsCommand
from application.commands.change_shopping_list_units.command_dto import ChangeShoppingListUnitsCommandDTO
from application.commands.remove_from_shopping_list.command import RemoveFromShoppingListCommand
from application.commands.remove_from_shopping_list.command_dto import RemoveFromShoppingListCommandDTO
from infrastructure import dependencies
from infrastructure.api.shared.serializers import ShoppingListItemSerializer
from infrastructure.api.shopping_list_item.serializer import ChangeUnitsSerializer


class ShoppingListItemView(APIView):
    def patch(self, request, item_id):
        serializer = ChangeUnitsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = ChangeShoppingListUnitsCommand(dependencies.get_repositories()).execute(
            ChangeShoppingListUnitsCommandDTO(item_id=item_id, units=serializer.validated_data["units"])
        )
        return Response(ShoppingListItemSerializer(item).data)

    def delete(self, request, item_id):
        RemoveFromShoppingListCommand(dependencies.get_repositories()).execute(RemoveFromShoppingListCommandDTO(item_id=item_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
