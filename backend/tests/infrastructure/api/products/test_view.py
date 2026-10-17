import pytest

pytestmark = pytest.mark.django_db


def test_add_product_with_existing_supplier(owner_client, salon):
    suppliers = owner_client.get("/api/suppliers/").json()

    response = owner_client.post(
        "/api/products/",
        {
            "name": "Bandas",
            "unit_price": "4.50",
            "uses_per_unit": 20,
            "units_in_stock": 2,
            "min_units": 1,
            "supplier_id": suppliers[0]["id"],
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["stock_uses"] == 40


def test_count_stock(owner_client, salon):
    response = owner_client.post(f"/api/products/{salon.oil.id}/count/", {"uses_in_stock": 7}, format="json")

    assert response.json()["stock_uses"] == 7
