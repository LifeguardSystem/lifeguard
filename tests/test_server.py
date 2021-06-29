import json
import unittest
from unittest.mock import MagicMock, patch

from lifeguard import NORMAL, PROBLEM
from lifeguard.server import (
    execute_validation,
    get_validation,
    get_status,
    get_status_complete,
)
from lifeguard.validations import ValidationResponse

test_validation = MagicMock(name="test_validation")
test_validation.return_value = ValidationResponse("test_validation", NORMAL, {})

VALIDATIONS = {"test_validation": {"ref": test_validation}}


class TestServer(unittest.TestCase):
    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.VALIDATIONS", VALIDATIONS)
    def test_execute_validation(self, mock_make_response):
        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        response = execute_validation("test_validation")
        self.assertEqual(response, mock_response)

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.traceback")
    @patch("lifeguard.server.logger")
    @patch("lifeguard.server.VALIDATIONS", VALIDATIONS)
    def test_execute_validation_with_error(
        self, mock_logger, mock_traceback, mock_make_response
    ):
        mock_traceback.format_exc.return_value = "traceback"
        mock_make_response.side_effect = Exception("exception")

        response = execute_validation("test_validation")
        self.assertEqual(response, json.dumps({"error": "traceback"}))
        mock_logger.error.assert_called_with(
            "error on execute validation %s",
            "test_validation",
            extra={"traceback": "traceback"},
        )

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.ValidationRepository")
    def test_get_validation_result(
        self, mock_validation_repository, mock_make_response
    ):

        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        mock_repository_instance = MagicMock(name="mock_repository_instance")
        mock_validation_repository.return_value = mock_repository_instance
        mock_repository_instance.fetch_last_validation_result.return_value = (
            ValidationResponse("test_validation", NORMAL, {})
        )

        response = get_validation("test_validation")
        self.assertEqual(response, mock_response)

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.ValidationRepository")
    def test_get_status(self, mock_validation_repository, mock_make_response):

        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        mock_repository_instance = MagicMock(name="mock_repository_instance")
        mock_validation_repository.return_value = mock_repository_instance
        mock_repository_instance.fetch_all_validation_results.return_value = [
            ValidationResponse("test_validation", PROBLEM, {})
        ]

        response = get_status()
        mock_make_response.assert_called_with(
            '{"status": "PROBLEM", "validations": [{"validation_name": "test_validation", "status": "PROBLEM", "details": {}, "settings": null}]}'
        )
        self.assertEqual(response, mock_response)

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.ValidationRepository")
    def test_get_status_validations_empty_when_normal(
        self, mock_validation_repository, mock_make_response
    ):

        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        mock_repository_instance = MagicMock(name="mock_repository_instance")
        mock_validation_repository.return_value = mock_repository_instance
        mock_repository_instance.fetch_all_validation_results.return_value = [
            ValidationResponse("test_validation", NORMAL, {})
        ]

        response = get_status()
        mock_make_response.assert_called_with('{"status": "NORMAL", "validations": []}')
        self.assertEqual(response, mock_response)

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.ValidationRepository")
    def test_get_status_complete(self, mock_validation_repository, mock_make_response):

        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        mock_repository_instance = MagicMock(name="mock_repository_instance")
        mock_validation_repository.return_value = mock_repository_instance
        mock_repository_instance.fetch_all_validation_results.return_value = [
            ValidationResponse("test_validation", NORMAL, {})
        ]

        response = get_status_complete()
        mock_make_response.assert_called_with(
            '{"status": "NORMAL", "validations": [{"validation_name": "test_validation", "status": "NORMAL", "details": {}, "settings": null}]}'
        )
        self.assertEqual(response, mock_response)

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.ValidationRepository")
    @patch("lifeguard.server.traceback")
    def test_get_status_on_exception(
        self, mock_traceback, mock_validation_repository, mock_make_response
    ):

        mock_traceback.format_exc.return_value = "traceback"

        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        mock_validation_repository.side_effect = [Exception("error")]

        response = get_status_complete()
        self.assertEqual(response, mock_response)
