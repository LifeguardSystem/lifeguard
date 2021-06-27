import unittest
from unittest.mock import ANY, MagicMock, patch

from lifeguard.controllers import (
    Response,
    load_custom_controllers,
    treat_response,
    configure_controller,
    render_template,
    Request,
    login_required,
)
from tests.fixtures.controllers.hello_controller import hello

mock_flask_request = MagicMock(name="flask_request")

MOCK_BASIC_AUTH = MagicMock(name="basic_auth")
MOCK_AUTHENTICATION_METHODS = {"basic_auth": MOCK_BASIC_AUTH}


class TestControllers(unittest.TestCase):
    @patch("lifeguard.controllers.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.controllers.logger")
    @patch("lifeguard.controllers.custom_controllers")
    def test_load_custom_controllers(self, mock_custom_controllers, mock_logger):
        load_custom_controllers()
        mock_logger.info.assert_any_call(
            "loading custom controller %s", "hello_controller"
        )
        mock_custom_controllers.add_url_rule.assert_called_with("/hello", "hello", ANY)
        self.assertEqual("hello", hello())

    @patch("lifeguard.controllers.FlaskResponse")
    @patch("lifeguard.controllers.render_template")
    def test_treat_response_with_template(
        self, mock_render_template, mock_flask_response
    ):
        mock_render_template.return_value = "template rendered"

        response = Response()
        response.template = "template.html"
        response.template_searchpath = "/templates"

        treat_response(response)

        mock_flask_response.assert_called_with(
            "template rendered", content_type="text/html", status=200
        )
        mock_render_template.assert_called_with("template.html", "/templates", data={})

    @patch("lifeguard.controllers.FlaskResponse")
    @patch("lifeguard.controllers.render_template")
    def test_treat_response_without_template(
        self, mock_render_template, mock_flask_response
    ):
        mock_render_template.return_value = "template rendered"

        response = Response()
        response.content = "body {}"
        response.content_type = "text/css"
        response.status = 404

        treat_response(response)

        mock_flask_response.assert_called_with(
            "body {}", content_type="text/css", status=404
        )
        mock_render_template.assert_not_called()

    def test_configure_controller_success_with_string(self):
        def test():
            return "str"

        self.assertEqual("str", configure_controller(test)())

    @patch("lifeguard.controllers.treat_response")
    def test_configure_controller_success_with_response(self, mock_treat_response):
        response = Response()

        def test():
            return response

        configure_controller(test)()
        mock_treat_response.assert_called_with(response)

    @patch("lifeguard.controllers.logger")
    @patch("lifeguard.controllers.traceback")
    def test_configure_controller_error(self, mock_traceback, mock_logger):
        mock_traceback.format_exc.return_value = "traceback"

        def test():
            raise Exception()

        configure_controller(test)()
        mock_logger.error.assert_called_with(
            "error on render dashboard index: %s",
            "",
            extra={"traceback": "traceback"},
        )

    @patch("lifeguard.controllers.jinja2")
    def test_render_template(self, mock_jinja2):

        template_loader = MagicMock(name="template_loader")
        mock_jinja2.FileSystemLoader.return_value = template_loader

        template_env = MagicMock(name="template_env")
        mock_jinja2.Environment.return_value = template_env

        template = MagicMock(name="template")
        template_env.get_template.return_value = template

        render_template("template", "searchpath")

        mock_jinja2.FileSystemLoader.assert_called_with(searchpath="searchpath")
        mock_jinja2.Environment.assert_called_with(loader=template_loader)
        template.render.assert_called()

    @patch("lifeguard.controllers.jinja2")
    def test_render_template_with_data(self, mock_jinja2):

        template_loader = MagicMock(name="template_loader")
        mock_jinja2.FileSystemLoader.return_value = template_loader

        template_env = MagicMock(name="template_env")
        mock_jinja2.Environment.return_value = template_env

        template = MagicMock(name="template")
        template_env.get_template.return_value = template

        render_template("template", "searchpath", data={"test": True})

        mock_jinja2.FileSystemLoader.assert_called_with(searchpath="searchpath")
        mock_jinja2.Environment.assert_called_with(loader=template_loader)
        template.render.assert_called_with(test=True)

    @patch("lifeguard.controllers.flask_request", mock_flask_request)
    def test_request_proxy(self):
        request = Request()
        mock_flask_request.json = "json"
        mock_flask_request.data = "data"
        mock_flask_request.form = "form"
        mock_flask_request.method = "method"
        mock_flask_request.args = "args"
        mock_flask_request.values = "values"

        self.assertEqual("json", request.json)
        self.assertEqual("data", request.data)
        self.assertEqual("form", request.form)
        self.assertEqual("method", request.method)
        self.assertEqual("args", request.args)
        self.assertEqual("values", request.values)

    @patch("lifeguard.controllers.AUTHENTICATION_METHODS", MOCK_AUTHENTICATION_METHODS)
    @patch("lifeguard.controllers.LIFEGUARD_CONTEXT")
    def test_login_required_wrap_controller(self, mock_lifeguard_context):

        mock_lifeguard_context.auth_method = "basic_auth"
        MOCK_AUTHENTICATION_METHODS["basic_auth"].return_value = False

        a_function = MagicMock(name="a_function")
        wrapped = login_required(a_function)

        self.assertFalse(wrapped())
        MOCK_AUTHENTICATION_METHODS["basic_auth"].assert_called_with((), {}, a_function)

    @patch("lifeguard.controllers.AUTHENTICATION_METHODS", MOCK_AUTHENTICATION_METHODS)
    @patch("lifeguard.controllers.LIFEGUARD_CONTEXT")
    def test_login_required_not_wrap_controller(self, mock_lifeguard_context):

        mock_lifeguard_context.auth_method = None

        a_function = MagicMock(name="a_function")
        a_function.return_value = 1
        wrapped = login_required(a_function)

        self.assertEqual(wrapped(), 1)
        MOCK_AUTHENTICATION_METHODS["basic_auth"].assert_not_called()
