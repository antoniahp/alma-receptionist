import pytest

pytestmark = pytest.mark.django_db


def test_shopping_list_flow(owner_client, salon):
    added = owner_client.post(
        "/api/shopping-list/",
        {"product": str(salon.oil.id), "store": "Druni", "title": "Aceite", "price": "9.50", "link": "https://druni.example/a", "units": 2},
        format="json",
    )
    assert added.status_code == 201
    item_id = added.json()["id"]

    changed = owner_client.patch(f"/api/shopping-list/{item_id}/", {"units": 3}, format="json")
    assert changed.json()["units"] == 3

    groups = owner_client.get("/api/shopping-list/").json()
    assert groups[0]["store"] == "Druni"
    assert groups[0]["is_supplier"] is False
    assert groups[0]["trusted"] is True
    assert groups[0]["total"] == "28.50"

    ordered = owner_client.post("/api/shopping-list/order/", {"store": "Druni", "bought_online": True}, format="json")
    assert ordered.status_code == 201
    assert ordered.json()["status"] == "sent"
    assert owner_client.get("/api/shopping-list/").json() == []


def test_supplier_store_is_recognised(owner_client, salon):
    owner_client.post("/api/shopping-list/", {"product": str(salon.oil.id), "store": salon.supplier.name, "price": "9.50"}, format="json")

    groups = owner_client.get("/api/shopping-list/").json()

    assert groups[0]["is_supplier"] is True


def test_remove_from_the_list(owner_client, salon):
    item_id = owner_client.post(
        "/api/shopping-list/", {"product": str(salon.oil.id), "store": "Druni", "price": "9.50"}, format="json"
    ).json()["id"]

    assert owner_client.delete(f"/api/shopping-list/{item_id}/").status_code == 204
    assert owner_client.get("/api/shopping-list/").json() == []


def test_clients_cannot_see_the_shopping_list(api_client, salon):
    assert api_client.get("/api/shopping-list/").status_code == 401


def test_long_google_shopping_links_are_accepted(owner_client, salon):
    google_link = (
        "https://www.google.com/search?ibp=oshop&q=Germaine%20de%20Capuccini%20Purexpert%20mascarilla%2075%20ml"
        "&prds=productid:551058035584092826,headlineOfferDocid:551058035584092826,imageDocid:17962151231997047208,pvt:hg"
        "&hl=es&gl=es&udm=28" + "&x=" + "a" * 1200
    )

    response = owner_client.post(
        "/api/shopping-list/", {"product": str(salon.oil.id), "store": "Druni", "price": "9.50", "link": google_link}, format="json"
    )

    assert response.status_code == 201


def test_amazon_group_has_a_single_cart_link(owner_client, salon):
    owner_client.post(
        "/api/shopping-list/",
        {"product": str(salon.oil.id), "store": "Amazon.es", "price": "9.50", "link": "https://www.amazon.es/dp/B0ABCDEF12", "units": 2},
        format="json",
    )

    group = owner_client.get("/api/shopping-list/").json()[0]

    assert group["cart_link"] == "https://www.amazon.es/gp/aws/cart/add.html?ASIN.1=B0ABCDEF12&Quantity.1=2"
