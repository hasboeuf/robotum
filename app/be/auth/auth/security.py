""" Security module
"""
import time

from jose import jwt, JWTError, ExpiredSignatureError

from auth.models import User


JWT_ISSUER = "robotum"
JWT_SECRET = "change_this"
JWT_LIFETIME_SECONDS = 60 * 60
JWT_ALGORITHM = "HS256"


def generate_token(user):
    timestamp = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "username": user.username,
        "admin": user.admin,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    options = {
        "verify_signature": False,
        "verify_iat": True,
        "verify_exp": True,
        "verify_iss": True,
        "require_iat": False,
        "require_exp": False,
        "require_iss": False,
    }

    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"], issuer=JWT_ISSUER, options=options)
    except JWTError as e:
        print("Invalid token")
        return None
    except JWTClaimsError as e:
        print("Wrong token")
        return None
