from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from domain.exceptions import InvalidEmail


class UpdateSupplierEmailCommand:
    """Cambia el correo al que se envían los pedidos de un proveedor."""

    def __init__(self, repositories):
        self.repositories = repositories

    def execute(self, dto):
        email = dto.email.strip().lower()
        try:
            validate_email(email)
        except ValidationError as error:
            raise InvalidEmail() from error
        supplier = self.repositories.suppliers.get(dto.supplier_id)
        supplier.email = email
        self.repositories.suppliers.save(supplier, ["email"])
        return supplier
