from typing import Any
from django.urls import resolve
from django.http import HttpRequest
import jwt
import uuid
import random
import os

import requests

PROTECTED_VIEWS = [
    "index",
    "add_todo",
    "edit_todo",
    "details_todo",
    "delete_todo",
    "user_profile",
]

EXCLUDED_VIEWS = ["logout"]


def token_verify(token: str) -> Any:
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
        request (HttpRequest)

    Returns:
        str | None: the name of route or None if not defined
    """
    match = resolve(request.path_info)
    route_name = match.url_name
    return route_name


def get_oauth_url(
    scope: str = "profile email",
    response_type: str = "code",
) -> str:
    url = f"{os.getenv("GOOGLE_OAUTH_URL")}?prompt=select_account&scope={scope}&redirect_uri={os.getenv("GOOGLE_REDIRECT_URL")}&response_type={response_type}&client_id={os.getenv("GOOGLE_CLIENT_ID")}"
    return url


def get_oauth_url_token(code: str) -> str:
    url = f"{os.getenv("GOOGLE_OAUTH_TOKEN_URL")}?code={code}&redirect_uri={os.getenv("GOOGLE_REDIRECT_URL")}&client_id={os.getenv("GOOGLE_CLIENT_ID")}&client_secret={os.getenv("GOOGLE_CLIENT_SECRET")}&grant_type=authorization_code"
    return url


def get_user_info_url() -> str:
    return str(os.getenv("GOOGLE_OAUTH_USER_INFO_URL"))


def get_oauth_token(code: str) -> Any:
    res = requests.post(
        get_oauth_url_token(code=code),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception("unable to get token")


def get_oauth_user(token: str) -> Any:
    res = requests.post(
        get_user_info_url(),
        headers={
            "Authorization": token,
        },
    )

    if res.status_code == 200:
        return res.json()
    else:
        raise Exception("unable to get user")
