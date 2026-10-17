from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from application.queries.get_available_slots.query import GetAvailableSlotsQuery
from application.queries.get_available_slots.query_dto import GetAvailableSlotsQueryDTO
from infrastructure import dependencies
from infrastructure.api.public_availability.serializer import AvailabilityFiltersSerializer, AvailabilitySerializer


class PublicAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = AvailabilityFiltersSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        service_id = filters.validated_data["service"]
        if dependencies.get_repositories().services.find_active(service_id) is None:
            return Response({"slots": []})
        slots = GetAvailableSlotsQuery(dependencies.get_repositories()).execute(
            GetAvailableSlotsQueryDTO(service_id=service_id, day=filters.validated_data["date"])
        )
        return Response(AvailabilitySerializer(slots).data)
