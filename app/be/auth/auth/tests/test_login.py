import pytest
from auth.models import User
from auth.tests.conftest import DEFAULT_USER, DEFAULT_PASSWORD
from auth.tests.utils import check_default_response


def test_login(client, create_user):
    response = client.post("v1/login", json={"username": DEFAULT_USER, "password": DEFAULT_PASSWORD})
    assert response.status_code == 200
    assert "token" in response.json
    assert response.json["admin"]


def test_login_400(client):
    response = client.post("v1/login", json={})
    assert response.status_code == 400
    check_default_response(response)


def test_login_404(client):
    response = client.post("v1/login", json={"username": "test", "password": "test"})
    assert response.status_code == 404
    check_default_response(response)
