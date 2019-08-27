""" API endpoints
"""
from auth.database import db_session
from auth.models import User


def login():
    """ todoc
    """


def logout():
    """ todoc
    """


def get_users():
    """ todoc
    """
    users = User.query.all()
    return {"users": [{"username": x.username, "admin": x.admin} for x in users]}, 200


def create_user(body):
    """ todoc
    """
    username = body["username"]
    password = body["password"]
    admin = body["admin"]

    user = User(username, password, admin)
    db_session.add(user)
    db_session.commit()
    return {"code": "OK", "message": "{} created".format(username)}, 200
