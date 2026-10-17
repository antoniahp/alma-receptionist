from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.order_from_store.command import OrderFromStoreCommand
from application.commands.order_from_store.command_dto import OrderFromStoreCommandDTO
from infrastructure import dependencies
from infrastructure.api.shared.serializers import PurchaseOrderSerializer
from infrastructure.api.shopping_list_order.serializer import OrderFromStoreSerializer


class OrderFromStoreView(APIView):
    def post(self, request):
        serializer = OrderFromStoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderFromStoreCommand(dependencies.get_repositories()).execute(OrderFromStoreCommandDTO(**serializer.validated_data))
        return Response(PurchaseOrderSerializer(order).data, status=status.HTTP_201_CREATED)
