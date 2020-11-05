import unittest
from unittest.mock import patch

from lifeguard import (
    ValidationResponse,
    change_status,
    load_validations,
    NORMAL,
    WARNING,
    PROBLEM,
    VALIDATIONS,
    VERSION,
    ACTION_STATUSES,
)


class TestValidationResponse(unittest.TestCase):
    def test_validation_response_object(self):
        details = {}
        settings = {}

        response = ValidationResponse("name", NORMAL, details, settings)

        self.assertEqual(response.validation_name, "name")
        self.assertEqual(response.status, "NORMAL")
        self.assertEqual(response.details, details)
        self.assertEqual(response.settings, settings)

    def test_validation_response_to_str(self):
        response = ValidationResponse("name", NORMAL, {}, {})
        self.assertEqual(
            str(response),
            "{'validation_name': 'name', 'status': 'NORMAL', 'details': {}, 'settings': {}}",
        )


class TestLifeguardCore(unittest.TestCase):
    def test_current_version(self):
        self.assertEqual(VERSION, "0.0.1")

    def test_statuses(self):
        self.assertEqual(NORMAL, "NORMAL")
        self.assertEqual(WARNING, "WARNING")
        self.assertEqual(PROBLEM, "PROBLEM")
        self.assertEqual(ACTION_STATUSES, [NORMAL, WARNING, PROBLEM])

    def test_change_status(self):
        self.assertEqual(change_status(NORMAL, NORMAL), NORMAL)
        self.assertEqual(change_status(NORMAL, WARNING), WARNING)
        self.assertEqual(change_status(PROBLEM, WARNING), PROBLEM)


class TestValidations(unittest.TestCase):
    @patch("lifeguard.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.logger")
    def test_load_validations(self, mock_logger):
        load_validations()
        mock_logger.info.assert_called_with("loading validation simple_validation")
        self.assertTrue("simple_validation" in VALIDATIONS)

    @patch("lifeguard.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.logger")
    def test_execute_validation(self, _mock_logger):
        load_validations()
        response = VALIDATIONS["simple_validation"]["ref"]()
        self.assertEqual(response.status, NORMAL)

    @patch("lifeguard.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.logger")
    def test_execute_validation_with_action(self, mock_logger):
        load_validations()
        VALIDATIONS["simple_with_action_validation"]["ref"]()
        mock_logger.info.assert_called_with(
            "executing action %s with result %s...",
            "simple_action",
            "{'validation_name': 'simple_with_action_validation', 'status': 'NORMAL', 'details': {}, 'settings': None}",
        )

    @patch("lifeguard.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.logger")
    @patch("lifeguard.traceback")
    def test_execute_validation_with_invalid_action(self, mock_traceback, mock_logger):
        mock_traceback.format_exc.return_value = "traceback"
        load_validations()
        VALIDATIONS["simple_with_invalid_action_validation"]["ref"]()
        mock_logger.warning.assert_called_with(
            "validation error %s: %s",
            "simple_with_invalid_action_validation",
            "invalid_action() takes 0 positional arguments but 1 was given",
            extra={"traceback": "traceback"},
        )
