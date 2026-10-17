import csv
import io

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView

from application.queries.export_finances.query import ExportFinancesQuery
from application.queries.export_finances.query_dto import ExportFinancesQueryDTO
from infrastructure import dependencies
from infrastructure.api.finances.serializer import FinancesQuerySerializer

HEADER = ["Fecha", "Tipo", "Concepto", "Categoría", "Forma de pago", "Importe"]


def spanish_amount(amount):
    return f"{amount:.2f}".replace(".", ",")


class FinancesExportView(APIView):
    def get(self, request):
        """CSV del mes para la gestoría. Separado por ';' y con BOM para que Excel lo abra bien en español."""
        params = FinancesQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        month = params.validated_data.get("month") or timezone.localdate()
        rows = ExportFinancesQuery(dependencies.get_repositories()).execute(ExportFinancesQueryDTO(month=month))

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(HEADER)
        for row in rows:
            writer.writerow(
                [
                    row["date"].strftime("%d/%m/%Y"),
                    row["type"],
                    row["concept"],
                    row["category"],
                    row["payment_method"],
                    spanish_amount(row["amount"]),
                ]
            )
        response = HttpResponse("﻿" + output.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="cuentas-{month:%Y-%m}.csv"'
        return response
