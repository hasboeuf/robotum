""" API endpoints
"""
from auth.models import User
from auth.security import generate_token, decode_token


def _get_bad_request():
    return {"code": "BAD_REQUEST", "message": "Bad request"}, 400


def login(body):
    """ todoc
    """
    try:
        username = body["username"]
        password = body["password"]
    except:
        return _get_bad_request()
    user = User.query.filter(User.username == username).first()
    if not user:
        return {"code": "NOT_FOUND", "message": "Wrong username/password"}, 404
    return {"token": generate_token(user), "admin": user.admin}, 200


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
    try:
        username = body["username"]
        password = body["password"]
        admin = body["admin"]
    except:
        return _get_bad_request()

    user = User(username, password, admin)
    try:
        user.add()
    except:
        return {"code": "BAD_REQUEST", "message": "Integrity error"}, 401
    return {"code": "OK", "message": "{} created".format(username)}, 200


def check(body):
    """ todoc
    """
    try:
        token = body["token"]
    except:
        return _get_bad_request()

    res = decode_token(body["token"])
    if res:
        return {"token": res}, 200
    return {"code": "BAD_TOKEN", "message": "Invalid token"}, 401
