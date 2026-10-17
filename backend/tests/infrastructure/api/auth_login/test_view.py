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


def login(api_client):
    get_user_model().objects.create_user("cris", password="secreta123")
    return api_client.post("/api/auth/login/", {"username": "cris", "password": "secreta123"}, format="json").json()["token"]


def test_a_fresh_session_opens_the_panel(api_client):
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {login(api_client)}")

    assert api_client.get("/api/dashboard/").status_code == 200


def test_an_old_session_asks_for_the_password_again(api_client, settings):
    from datetime import timedelta

    from django.utils import timezone
    from rest_framework.authtoken.models import Token

    token = login(api_client)
    Token.objects.filter(key=token).update(created=timezone.now() - timedelta(hours=settings.PANEL_SESSION_HOURS + 1))
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    assert api_client.get("/api/dashboard/").status_code == 401
    assert not Token.objects.filter(key=token).exists()



def test_logging_in_after_the_session_expired_opens_a_new_one(api_client, settings):
    from datetime import timedelta

    from django.utils import timezone
    from rest_framework.authtoken.models import Token

    first = login(api_client)
    Token.objects.filter(key=first).update(created=timezone.now() - timedelta(hours=settings.PANEL_SESSION_HOURS + 1))
    second = api_client.post("/api/auth/login/", {"username": "cris", "password": "secreta123"}, format="json").json()["token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {second}")

    assert first != second
    assert api_client.get("/api/dashboard/").status_code == 200
