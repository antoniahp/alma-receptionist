from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.book_online_appointment.command import BookOnlineAppointmentCommand
from application.commands.book_online_appointment.command_dto import BookOnlineAppointmentCommandDTO
from infrastructure import dependencies
from infrastructure.api.public_booking.serializer import BookedAppointmentSerializer, PublicBookingSerializer


class PublicBookingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PublicBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        appointment = BookOnlineAppointmentCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
            BookOnlineAppointmentCommandDTO(
                service_id=data["service"],
                start=data["start"],
                name=data["name"],
                phone=data["phone"],
                privacy_accepted=data["privacy_accepted"],
            )
        )
        return Response(BookedAppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
