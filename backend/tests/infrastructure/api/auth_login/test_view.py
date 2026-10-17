import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_login_returns_token(api_client):
    get_user_model().objects.create_user("cris", password="secreta123")

    response = api_client.post("/api/auth/login/", {"username": "cris", "password": "secreta123"}, format="json")

    assert response.status_code == 200
    assert response.json()["token"]


def test_wrong_password(api_client):
    get_user_model().objects.create_user("cris", password="secreta123")

    response = api_client.post("/api/auth/login/", {"username": "cris", "password": "mal"}, format="json")

    assert response.status_code == 400


@pytest.mark.parametrize("url", ["/api/appointments/", "/api/dashboard/", "/api/products/forecast/", "/api/help-requests/", "/api/status/"])
def test_panel_needs_login(api_client, url):
    assert api_client.get(url).status_code == 401
