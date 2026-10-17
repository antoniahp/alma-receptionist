from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.commands.book_appointment.command import BookAppointmentCommand
from application.commands.book_appointment.command_dto import BookAppointmentCommandDTO
from application.queries.list_appointments.query import ListAppointmentsQuery
from application.queries.list_appointments.query_dto import ListAppointmentsQueryDTO
from domain.entities import Appointment
from infrastructure import dependencies
from infrastructure.api.appointments.serializer import AppointmentFiltersSerializer, CreateAppointmentSerializer
from infrastructure.api.shared.serializers import AppointmentSerializer


class AppointmentListView(APIView):
    def get(self, request):
        params = {
            "date_from": request.query_params.get("from"),
            "date_to": request.query_params.get("to"),
            "status": request.query_params.get("status"),
        }
        # Los parámetros vacíos no cuentan como filtro
        params = {key: value for key, value in params.items() if value}
        filters = AppointmentFiltersSerializer(data=params)
        filters.is_valid(raise_exception=True)
        data = filters.validated_data
        statuses = data["status"].split(",") if data.get("status") else []
        repositories = dependencies.get_repositories()
        appointments = ListAppointmentsQuery(repositories).execute(
            ListAppointmentsQueryDTO(date_from=data.get("date_from"), date_to=data.get("date_to"), statuses=statuses)
        )
        pack_pairs = repositories.packs.active_pairs({appointment.client_id for appointment in appointments})
        return Response(AppointmentSerializer(appointments, many=True, context={"pack_pairs": pack_pairs}).data)

    def post(self, request):
        serializer = CreateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        appointment = BookAppointmentCommand(dependencies.get_repositories(), dependencies.get_message_service()).execute(
            BookAppointmentCommandDTO(
                client_id=data["client"],
                service_id=data["service"],
                start=data["start"],
                source=Appointment.SOURCE_OWNER,
                notes=data["notes"],
            )
        )
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
