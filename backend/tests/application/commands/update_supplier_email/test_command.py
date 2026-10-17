import pytest

from application.commands.update_supplier_email.command import UpdateSupplierEmailCommand
from application.commands.update_supplier_email.command_dto import UpdateSupplierEmailCommandDTO
from domain.exceptions import InvalidEmail

pytestmark = pytest.mark.django_db


def test_updates_the_email(repositories, salon):
    supplier = UpdateSupplierEmailCommand(repositories).execute(
        UpdateSupplierEmailCommandDTO(supplier_id=salon.supplier.id, email="  Pedidos@Proveedor.com ")
    )

    salon.supplier.refresh_from_db()
    assert supplier.email == "pedidos@proveedor.com"
    assert salon.supplier.email == "pedidos@proveedor.com"


def test_rejects_an_invalid_email(repositories, salon):
    old_email = salon.supplier.email

    with pytest.raises(InvalidEmail):
        UpdateSupplierEmailCommand(repositories).execute(
            UpdateSupplierEmailCommandDTO(supplier_id=salon.supplier.id, email="no-es-un-correo")
        )

    salon.supplier.refresh_from_db()
    assert salon.supplier.email == old_email
