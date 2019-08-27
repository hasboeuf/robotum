import pytest
from auth.models import User
from auth.tests.conftest import DEFAULT_USER, DEFAULT_PASSWORD
from auth.tests.utils import check_default_response


def test_create_user(client):
    try:
        response = client.post(
            "v1/users",
            json={
                "username": DEFAULT_USER,
                "password": DEFAULT_PASSWORD,
                "admin": False,
            },
        )
        assert response.status_code == 200
        user = User.get(DEFAULT_USER)
        assert user.username == DEFAULT_USER
        assert user.password == DEFAULT_PASSWORD
        assert user.admin == False
    finally:
        User.delete_all()


def test_create_user_400(client):
    response = client.post(
        "v1/users",
        json={"name": DEFAULT_USER, "password": DEFAULT_PASSWORD, "admin": False},
    )
    assert response.status_code == 400
    check_default_response(response)


def test_create_user_twice_401(client):
    try:
        response = client.post(
            "v1/users",
            json={
                "username": DEFAULT_USER,
                "password": DEFAULT_PASSWORD,
                "admin": False,
            },
        )
        assert response.status_code == 200
        response = client.post(
            "v1/users",
            json={
                "username": DEFAULT_USER,
                "password": DEFAULT_PASSWORD,
                "admin": False,
            },
        )
        assert response.status_code == 401
        check_default_response(response)
    finally:
        User.delete_all()
