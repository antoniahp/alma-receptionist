import uuid

import pytest

pytestmark = pytest.mark.django_db


def test_owner_changes_the_supplier_email(owner_client, salon):
    response = owner_client.patch(f"/api/suppliers/{salon.supplier.id}/", {"email": "pedidos@proveedor.com"}, format="json")

    assert response.status_code == 200
    assert response.json()["email"] == "pedidos@proveedor.com"


def test_invalid_email_returns_a_clear_error(owner_client, salon):
    response = owner_client.patch(f"/api/suppliers/{salon.supplier.id}/", {"email": "hola"}, format="json")

    assert response.status_code == 400
    assert "correo" in response.json()["detail"]


def test_unknown_supplier_returns_404(owner_client, salon):
    response = owner_client.patch(f"/api/suppliers/{uuid.uuid4()}/", {"email": "pedidos@proveedor.com"}, format="json")

    assert response.status_code == 404
