from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.create_product.command import CreateProductCommand
from application.commands.create_product.command_dto import CreateProductCommandDTO
from infrastructure import dependencies
from infrastructure.api.products.serializer import CreateProductSerializer, ProductSerializer


class ProductListView(APIView):
    def post(self, request):
        serializer = CreateProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = CreateProductCommand(dependencies.get_repositories()).execute(CreateProductCommandDTO(**serializer.validated_data))
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
