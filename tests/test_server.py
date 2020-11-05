import json
import unittest
from unittest.mock import MagicMock, patch

from lifeguard import NORMAL
from lifeguard.server import execute_validation
from lifeguard.validations import ValidationResponse

test_validation = MagicMock(name="test_validation")
test_validation.return_value = ValidationResponse("test_validation", NORMAL, {})

VALIDATIONS = {"test_validation": {"ref": test_validation}}


class TestServer(unittest.TestCase):
    @patch("lifeguard.server.make_response")
    def test_execute_validation(self, mock_make_response):
        mock_response = MagicMock(name="mock_response")
        mock_make_response.return_value = mock_response

        response = execute_validation("test_validation")
        self.assertEqual(response, mock_response)

    @patch("lifeguard.server.make_response")
    @patch("lifeguard.server.traceback")
    @patch("lifeguard.server.logger")
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
