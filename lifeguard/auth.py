"""
Auth methods
"""
import base64

from flask import Response as FlaskResponse
from flask import request as flask_request
from flask import session as flask_session

from lifeguard.context import LIFEGUARD_CONTEXT

BASIC_AUTH_METHOD = "basic_auth"


def _get_credentials(authorization_header):
    encoded_uname_pass = authorization_header.split()[-1]
    return base64.b64decode(encoded_uname_pass).decode("utf-8").split(":")


def basic_auth_login(authorization_header):
    """
    Basic auth method
    """
    username, password = _get_credentials(authorization_header)
    return LIFEGUARD_CONTEXT.valid_user(username, password)


def basic_auth_login_required_implementation(args, kwargs, function):
    """
    Baic Auth Login Implementation
    """
    authorization_header = flask_request.headers.get("Authorization")
    if authorization_header and basic_auth_login(authorization_header):
        flask_session["user"], _ = _get_credentials(authorization_header)
        return function(*args, **kwargs)
    response = FlaskResponse()
    response.headers["WWW-Authenticate"] = "Basic"
    return response, 401


AUTHENTICATION_METHODS = {BASIC_AUTH_METHOD: basic_auth_login_required_implementation}
