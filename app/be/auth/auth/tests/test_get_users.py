import pytest
from auth.models import User
from auth.tests.conftest import DEFAULT_USER


def test_get_users_none(client):
    response = client.get("v1/users")
    assert response.status_code == 200
    assert response.json == {"users": []}


def test_get_users_one(client, create_user):
    response = client.get("v1/users")
    assert response.status_code == 200
    assert response.json == {"users": [{"admin": True, "username": DEFAULT_USER}]}
