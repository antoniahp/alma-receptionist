from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructure import dependencies
from infrastructure.api.suppliers.serializer import SupplierSerializer


class SupplierListView(APIView):
    def get(self, request):
        suppliers = sorted(dependencies.get_repositories().suppliers.list(), key=lambda supplier: supplier.name.lower())
        return Response(SupplierSerializer(suppliers, many=True).data)
