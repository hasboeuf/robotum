import pytest
from auth.models import User
from auth.tests.conftest import DEFAULT_USER, DEFAULT_PASSWORD
from auth.tests.utils import check_default_response


def test_check(client, create_user):
    response = client.post("v1/login", json={"username": DEFAULT_USER, "password": DEFAULT_PASSWORD})
    token = response.json["token"]
    response = client.post("v1/check", json={"token": token})
    assert response.status_code == 200
    assert response.json["token"]
    assert response.json["token"]["iss"]
    assert response.json["token"]["iat"]
    assert response.json["token"]["exp"]
    assert response.json["token"]["username"] == DEFAULT_USER
    assert response.json["token"]["admin"] == True


def test_check_400(client, create_user):
    response = client.post("v1/check", json={"tokn": ""})
    assert response.status_code == 400
    check_default_response(response)


def test_check_401(client, create_user):
    response = client.post("v1/check", json={"token": "invalid"})
    assert response.status_code == 401
    check_default_response(response)
