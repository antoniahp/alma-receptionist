from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.update_supplier_email.command import UpdateSupplierEmailCommand
from application.commands.update_supplier_email.command_dto import UpdateSupplierEmailCommandDTO
from infrastructure import dependencies
from infrastructure.api.shared.serializers import SupplierSerializer
from infrastructure.api.supplier_detail.serializer import UpdateSupplierEmailSerializer


class SupplierDetailView(APIView):
    def patch(self, request, supplier_id):
        serializer = UpdateSupplierEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supplier = UpdateSupplierEmailCommand(dependencies.get_repositories()).execute(
            UpdateSupplierEmailCommandDTO(supplier_id=supplier_id, email=serializer.validated_data["email"])
        )
        return Response(SupplierSerializer(supplier).data)
