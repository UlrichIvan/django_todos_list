from django.urls import resolve
from django.http import HttpRequest
import jwt
import uuid
import random
import os

PROTECTED_VIEWS = [
    "index",
    "add_todo",
    "edit_todo",
    "details_todo",
    "delete_todo",
]

EXCLUDED_VIEWS = ["logout"]


def token_verify(token: str) -> any:
    """secode token of user

    Args:
        token (str): token encoded

    Returns:
        any: False if token is mistake and value decoded if is correct
    """
    try:
        token_decoded = jwt.decode(
            token, os.getenv("JWT_KEY"), algorithms=os.getenv("JWT_ALGO")
        )
        return token_decoded
    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError):
        return False


def get_code() -> str:
    """return the random code

    Returns:
        str: the random code
    """
    code_long = "".join(str(uuid.uuid4()).split("-"))
    code = code_long[0 : random.randint(8, 10)]
    return code.upper()


def get_jwt_token(payload: dict) -> str:
    """return the token value of token from payload

    Args:
        payload (dict): payload value

    Returns:
        str: token generated
    """
    return jwt.encode(payload, os.getenv("JWT_KEY"), algorithm=os.getenv("JWT_ALGO"))


def get_route_name(request: HttpRequest) -> str | None:
    """return the name of current route request

    Args:
        request (HttpRequest): _description_

    Returns:
        str | None: the name of route or None if not defined
    """
    match = resolve(request.path_info)
    route_name = match.url_name
    return route_name
