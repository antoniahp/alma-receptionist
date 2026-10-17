from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.approve_order.command import ApproveOrderCommand
from application.commands.approve_order.command_dto import ApproveOrderCommandDTO
from application.commands.discard_order.command import DiscardOrderCommand
from application.commands.discard_order.command_dto import DiscardOrderCommandDTO
from application.commands.generate_order_drafts.command import GenerateOrderDraftsCommand
from application.commands.generate_order_drafts.command_dto import GenerateOrderDraftsCommandDTO
from application.commands.receive_order.command import ReceiveOrderCommand
from application.commands.receive_order.command_dto import ReceiveOrderCommandDTO
from infrastructure import dependencies
from infrastructure.api.purchase_order_actions.serializer import PurchaseOrderSerializer


class GenerateOrderDraftsView(APIView):
    def post(self, request):
        drafts = GenerateOrderDraftsCommand(dependencies.get_repositories(), dependencies.get_language_model_service()).execute(
            GenerateOrderDraftsCommandDTO()
        )
        return Response(PurchaseOrderSerializer(drafts, many=True).data)


class ApproveOrderView(APIView):
    def post(self, request, order_id):
        order = ApproveOrderCommand(dependencies.get_repositories(), dependencies.get_email_service()).execute(
            ApproveOrderCommandDTO(order_id=order_id)
        )
        return Response(PurchaseOrderSerializer(order).data)


class ReceiveOrderView(APIView):
    def post(self, request, order_id):
        order = ReceiveOrderCommand(dependencies.get_repositories()).execute(ReceiveOrderCommandDTO(order_id=order_id))
        return Response(PurchaseOrderSerializer(order).data)


class DiscardOrderView(APIView):
    def post(self, request, order_id):
        order = DiscardOrderCommand(dependencies.get_repositories()).execute(DiscardOrderCommandDTO(order_id=order_id))
        return Response(PurchaseOrderSerializer(order).data)
