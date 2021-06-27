import os
import sys
import traceback
from functools import wraps

import jinja2
from flask import Blueprint
from flask import Response as FlaskResponse
from flask import request as flask_request

from lifeguard.auth import AUTHENTICATION_METHODS
from lifeguard.context import LIFEGUARD_CONTEXT
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY

custom_controllers = Blueprint("custom", __name__)


def render_template(template, searchpath, data=None):

    if not data:
        data = {}

    template_loader = jinja2.FileSystemLoader(searchpath=searchpath)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template)
    return template.render(**data)


class Request:
    @property
    def json(self):
        return flask_request.json

    @property
    def data(self):
        return flask_request.data

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


class Response:
    def __init__(self):
        self._content_type = "text/html"
        self._content = None
        self._template = None
        self._template_searchpath = None
        self._status = 200
        self._data = {}

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
    custom_controllers.add_url_rule(
        path, endpoint, configure_controller(login_required(function)), **options
    )


def load_custom_controllers():
    """
    Load custom controllers from application path
    """

    sys.path.append(LIFEGUARD_DIRECTORY)

    if not os.path.exists(os.path.join(LIFEGUARD_DIRECTORY, "controllers")):
        return

    for controller_file in os.listdir(os.path.join(LIFEGUARD_DIRECTORY, "controllers")):
        if controller_file.endswith("_controller.py"):
            controller_module_name = controller_file.replace(".py", "")
            logger.info("loading custom controller %s", controller_module_name)

            module = "controllers.%s" % (controller_module_name)
            if module not in sys.modules:
                __import__(module)


def treat_response(response):
    content = response.content
    if response.template:
        content = render_template(
            response.template, response.template_searchpath, data=response.data
        )

    return FlaskResponse(
        content, content_type=response.content_type, status=response.status
    )


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
