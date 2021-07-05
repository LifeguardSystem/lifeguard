import unittest

from unittest.mock import patch

from lifeguard import NORMAL
from lifeguard.validations import ValidationResponse, load_validations, VALIDATIONS


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


class TestValidations(unittest.TestCase):
    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    def test_load_validations(self, mock_logger):
        load_validations()
        mock_logger.info.assert_any_call("loading validation %s", "simple_validation")
        self.assertTrue("simple_validation" in VALIDATIONS)

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    def test_execute_validation(self, _mock_logger):
        load_validations()
        response = VALIDATIONS["simple_validation"]["ref"]()
        self.assertEqual(response.status, NORMAL)
        self.assertEqual(VALIDATIONS["simple_validation"]["settings"], {})

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    def test_execute_validation_with_action(self, mock_logger):
        load_validations()
        VALIDATIONS["simple_with_action_validation"]["ref"]()
        mock_logger.info.assert_called_with(
            "executing action %s with result %s...",
            "simple_action",
            "{'validation_name': 'simple_with_action_validation', 'status': 'NORMAL', 'details': {}, 'settings': None}",
        )

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch(
        "lifeguard.validations.LIFEGUARD_RUN_ONLY_VALIDATIONS",
        ["simple_with_action_validation"],
    )
    @patch("lifeguard.validations.logger")
    def test_execute_validation_because_in_list(self, mock_logger):
        load_validations()
        self.assertIsNotNone(VALIDATIONS["simple_with_action_validation"]["ref"]())
        mock_logger.info.assert_called_with(
            "executing action %s with result %s...",
            "simple_action",
            "{'validation_name': 'simple_with_action_validation', 'status': 'NORMAL', 'details': {}, 'settings': None}",
        )

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch(
        "lifeguard.validations.LIFEGUARD_RUN_ONLY_VALIDATIONS",
        ["simple_validation"],
    )
    @patch("lifeguard.validations.logger")
    def test_not_execute_validation_because_not_in_list(self, mock_logger):
        load_validations()
        self.assertIsNone(VALIDATIONS["simple_with_action_validation"]["ref"]())
        mock_logger.info.assert_called_with(
            "validation %s not in LIFEGUARD_RUN_ONLY_VALIDATIONS",
            "simple_with_action_validation",
        )

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch(
        "lifeguard.validations.LIFEGUARD_SKIP_VALIDATIONS",
        ["simple_validation"],
    )
    @patch("lifeguard.validations.logger")
    def test_execute_validation_because_not_in_skip_list(self, mock_logger):
        load_validations()
        self.assertIsNotNone(VALIDATIONS["simple_with_action_validation"]["ref"]())
        mock_logger.info.assert_called_with(
            "executing action %s with result %s...",
            "simple_action",
            "{'validation_name': 'simple_with_action_validation', 'status': 'NORMAL', 'details': {}, 'settings': None}",
        )

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch(
        "lifeguard.validations.LIFEGUARD_SKIP_VALIDATIONS",
        ["simple_with_action_validation"],
    )
    @patch("lifeguard.validations.logger")
    def test_not_execute_validation_because_in_skip_list(self, mock_logger):
        load_validations()
        self.assertIsNone(VALIDATIONS["simple_with_action_validation"]["ref"]())
        mock_logger.info.assert_called_with(
            "validation %s in LIFEGUARD_SKIP_VALIDATIONS",
            "simple_with_action_validation",
        )

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    @patch("lifeguard.validations.traceback")
    def test_execute_validation_with_invalid_action(self, mock_traceback, mock_logger):
        mock_traceback.format_exc.return_value = "traceback"
        load_validations()
        VALIDATIONS["simple_with_invalid_action_validation"]["ref"]()
        mock_logger.warning.assert_called_with(
            "validation error %s: %s",
            "simple_with_invalid_action_validation",
            "invalid_action() takes 0 positional arguments but 2 were given",
            extra={"traceback": "traceback"},
        )
