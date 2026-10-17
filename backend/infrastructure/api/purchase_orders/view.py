from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.update_order_draft.command import UpdateOrderDraftCommand
from application.commands.update_order_draft.command_dto import UpdateOrderDraftCommandDTO
from application.queries.list_purchase_orders.query import ListPurchaseOrdersQuery
from application.queries.list_purchase_orders.query_dto import ListPurchaseOrdersQueryDTO
from infrastructure import dependencies
from infrastructure.api.purchase_orders.serializer import UpdateOrderDraftSerializer
from infrastructure.api.shared.serializers import PurchaseOrderSerializer


class PurchaseOrderListView(APIView):
    def get(self, request):
        status_param = request.query_params.get("status", "")
        statuses = [value for value in status_param.split(",") if value]
        orders = ListPurchaseOrdersQuery(dependencies.get_repositories()).execute(ListPurchaseOrdersQueryDTO(statuses=statuses))
        return Response(PurchaseOrderSerializer(orders, many=True).data)


class PurchaseOrderDetailView(APIView):
    def patch(self, request, order_id):
        serializer = UpdateOrderDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = UpdateOrderDraftCommand(dependencies.get_repositories()).execute(
            UpdateOrderDraftCommandDTO(order_id=order_id, **serializer.validated_data)
        )
        return Response(PurchaseOrderSerializer(order).data)
