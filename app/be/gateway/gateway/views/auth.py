""" Auth endpoints
"""
import requests


def login(body):
    """ todoc
    """
    response = requests.post("http://127.0.0.1:8081/v1/login", json=body)
    return response.json(), response.status_code


def logout():
    """ todoc
    """
