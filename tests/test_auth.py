import unittest
from unittest.mock import MagicMock, patch

from lifeguard.auth import (
    basic_auth_login,
    basic_auth_login_required_implementation,
    AUTHENTICATION_METHODS,
)
from lifeguard.context import LifeguardContext

lifeguard_context = LifeguardContext()
lifeguard_context.users = [{"username": "test", "password": "pass"}]


class TestAuth(unittest.TestCase):
    @patch("lifeguard.auth.LIFEGUARD_CONTEXT", lifeguard_context)
    def test_auth_valid_user(self):
        header = "Basic dGVzdDpwYXNz"

        self.assertListEqual(
            basic_auth_login(header), [{"username": "test", "password": "pass"}]
        )

    @patch("lifeguard.auth.LIFEGUARD_CONTEXT", lifeguard_context)
    def test_auth_header(self):
        header = "Basic YTpi dGVzdDpwYXNz"

        self.assertListEqual(
            basic_auth_login(header), [{"username": "test", "password": "pass"}]
        )

    def test_auth_invalid_user(self):
        header = "Basic YTpi"

        self.assertFalse(basic_auth_login(header), [])

    @patch("lifeguard.auth.FlaskResponse")
    @patch("lifeguard.auth.flask_request", spec={})
    @patch("lifeguard.auth.basic_auth_login")
    def test_basic_auth_login_required_implementation_call_function(
        self, mock_login, mock_request, _mock_response
    ):
        args = MagicMock(name="args")
        kwargs = MagicMock(name="kwargs")
        function = MagicMock(name="function")

        mock_request.headers = MagicMock(name="headers")
        mock_request.headers.get.return_value = "returned_get"

        mock_login.return_value = True

        function.return_value = False

        self.assertFalse(
            basic_auth_login_required_implementation(args, kwargs, function)
        )

        function.assert_called()
        mock_request.headers.get.assert_called_with("Authorization")
        mock_login.assert_called_with("returned_get")

    @patch("lifeguard.auth.FlaskResponse")
    @patch("lifeguard.auth.flask_request", spec={})
    @patch("lifeguard.auth.basic_auth_login")
    def test_basic_auth_login_required_implementation_return_401(
        self, mock_login, mock_request, mock_response
    ):
        args = MagicMock(name="args")
        kwargs = MagicMock(name="kwargs")
        function = MagicMock(name="function")

        mock_request.headers = MagicMock(name="headers")
        mock_request.headers.get.return_value = "returned_get"

        mock_login.return_value = False

        response = MagicMock(name="response")
        response.headers = {}
        mock_response.return_value = response

        self.assertEqual(
            basic_auth_login_required_implementation(args, kwargs, function),
            (response, 401),
        )

        self.assertDictEqual(response.headers, {"WWW-Authenticate": "Basic"})

        function.assert_not_called()
        mock_request.headers.get.assert_called_with("Authorization")
        mock_login.assert_called_with("returned_get")

    def test_authentication_methods(self):
        self.assertEqual(
            AUTHENTICATION_METHODS["basic_auth"],
            basic_auth_login_required_implementation,
        )
