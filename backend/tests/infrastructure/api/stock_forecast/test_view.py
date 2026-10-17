import pytest

pytestmark = pytest.mark.django_db


def test_forecast_fields(owner_client, salon):
    row = owner_client.get("/api/products/forecast/").json()[0]

    assert row["name"] == "Aceite de almendras"
    assert row["supplier_name"] == "Aromas del Sur"
    assert row["stock_uses"] == 4
    assert row["status"] == "watch"
    assert row["runs_out_for"] is None
