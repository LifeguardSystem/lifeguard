"""
Implementation of contollers helpers
"""
import os
import sys
import traceback
from functools import wraps
from os.path import join

import jinja2
from flask import Blueprint
from flask import Response as FlaskResponse
from flask import request as flask_request
from flask import session as flask_session
from flask import redirect as flask_redirect

from lifeguard.auth import AUTHENTICATION_METHODS
from lifeguard.context import LIFEGUARD_CONTEXT
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY
from lifeguard.utils import build_import

custom_controllers = Blueprint("custom", __name__)


def build_content_from_template(template, searchpath, data=None):
    if not data:
        data = {}

    template_loader = jinja2.FileSystemLoader(searchpath=searchpath)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template)
    return template.render(**data)


def render_template(template, data=None, headers=None, searchpath=None):
    """
    render template used in contollers
    """

    if not searchpath:
        searchpath = str(join(LIFEGUARD_DIRECTORY, "templates"))

    response = Response()
    response.template = template
    response.template_searchpath = searchpath
    response.data = data
    response.headers = headers
    return response


def send_status(status):
    response = Response()
    response.status = status
    return response


class Session:
    def __getitem__(self, key):
        return flask_session[key]

    def __setitem__(self, key, value):
        flask_session[key] = value

    def get(self, key):
        return flask_session.get(key)


class Request:
    @property
    def json(self):
        return flask_request.json

    @property
    def data(self):
        return flask_request.data

    @property
    def headers(self):
        return flask_request.headers

    @property
    def form(self):
        return flask_request.form

    @property
    def method(self):
        return flask_request.method

    @property
    def args(self):
        return flask_request.args

    @property
    def values(self):
        return flask_request.values

    @property
    def cookies(self):
        return flask_request.cookies


class Response:
    def __init__(self):
        self._content_type = "text/html"
        self._content = None
        self._template = None
        self._template_searchpath = None
        self._status = 200
        self._data = {}
        self._headers = {}
        self._cookies = {}

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    @property
    def template_searchpath(self):
        return self._template_searchpath

    @template_searchpath.setter
    def template_searchpath(self, value):
        self._template_searchpath = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, value):
        self._cookies = value

    def set_cookie(self, key, value, options=None):
        if not options:
            options = {}
        options["value"] = value
        self._cookies[key] = options


def redirect(location, code=302):
    return flask_redirect(location, code)


def login_required(function):
    """
    Decorator for login
    """

    @wraps(function)
    def wrapped(*args, **kwargs):
        if LIFEGUARD_CONTEXT.auth_method in AUTHENTICATION_METHODS:
            return AUTHENTICATION_METHODS[LIFEGUARD_CONTEXT.auth_method](
                args, kwargs, function
            )
        return function(*args, **kwargs)

    return wrapped


def register_custom_controller(path, function, options):
    endpoint = options.pop("endpoint", function.__name__)
    skip_login = options.pop("skip_login", False)

    if not skip_login:
        function = login_required(function)

    custom_controllers.add_url_rule(
        path, endpoint, configure_controller(function), **options
    )


def load_custom_controllers():
    """
    Load custom controllers from application path
    """
    sys.path.append(LIFEGUARD_DIRECTORY)

    if not os.path.exists(os.path.join(LIFEGUARD_DIRECTORY, "controllers")):
        return
    for root, _dirs, files in os.walk(os.path.join(LIFEGUARD_DIRECTORY, "controllers")):
        root = os.path.relpath(root, os.path.join(LIFEGUARD_DIRECTORY))
        for controller_file in files:
            if controller_file.endswith("_controller.py"):
                controller_module_name = (
                    f'{build_import(root, controller_file.replace(".py", ""))}'
                )
                logger.info(
                    "loading custom controller %s", controller_file.replace(".py", "")
                )

                module = "%s" % (controller_module_name)
                if module not in sys.modules:
                    __import__(module)


def treat_response(response):
    content = response.content
    if response.template:
        content = build_content_from_template(
            response.template, response.template_searchpath, data=response.data
        )

    flask_response = FlaskResponse(
        content,
        content_type=response.content_type,
        status=response.status,
        headers=response.headers,
    )

    for key in response.cookies.keys():
        value = response.cookies[key].pop("value")
        flask_response.set_cookie(key, value, **response.cookies[key])

    return flask_response


def configure_controller(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            response = function(*args, **kwargs)

            if isinstance(response, Response):
                return treat_response(response)
            return response
        except Exception as error:
            logger.error(
                "error on render dashboard index: %s",
                str(error),
                extra={"traceback": traceback.format_exc()},
            )

    return wrapped


def controller(path, **options):
    """
    Decorator to configure a custom controller
    """

    def function_reference(decorated):
        @wraps(decorated)
        def wrapped(*args, **kwargs):
            return decorated(*args, **kwargs)

        register_custom_controller(path, decorated, options)
        return wrapped

    return function_reference


request = Request()
session = Session()
