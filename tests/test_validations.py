import unittest

from unittest.mock import patch, call

from lifeguard import NORMAL, PROBLEM
from lifeguard.validations import (
    ValidationResponse,
    load_validations,
    VALIDATIONS,
)

from tests.fixtures.validations.simple_validation_with_action_on_errors import (
    ON_ERROR_ACTION_MOCK,
)


class TestValidationResponse(unittest.TestCase):
    def test_validation_response_object(self):
        details = {}
        settings = {}

        response = ValidationResponse(NORMAL, details, settings, validation_name="name")

        self.assertEqual(response.validation_name, "name")
        self.assertEqual(response.status, "NORMAL")
        self.assertEqual(response.details, details)
        self.assertEqual(response.settings, settings)

    def test_validation_response_to_str(self):
        response = ValidationResponse(NORMAL, {}, {}, validation_name="name")
        self.assertEqual(
            str(response),
            "{'validation_name': 'name', 'status': 'NORMAL', 'details': {}, 'settings': {}}",
        )

    def test_validate_status_value(self):
        with self.assertRaises(ValueError) as error:
            ValidationResponse("INVALID", {}, {})

        self.assertEquals(str(error.exception), "INVALID is not a valid status")


class TestValidations(unittest.TestCase):
    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    def test_load_validations(self, mock_logger):
        load_validations()
        mock_logger.info.assert_any_call("loading validation %s", "simple_validation")
        self.assertTrue("simple_validation" in VALIDATIONS)

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    def test_load_validations_subdir(self, mock_logger):
        load_validations()
        mock_logger.info.assert_any_call(
            "loading validation %s", "simple_subdir_validation"
        )
        self.assertTrue("simple_subdir_validation" in VALIDATIONS)

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
    @patch("tests.fixtures.validations.shared.common_validation.logger")
    def test_execute_validation_with_action_defined_from_yaml(self, mock_logger):
        load_validations()
        response = VALIDATIONS["simple_validation_with_action_in_yaml"]["ref"]()
        self.assertEqual(response.status, NORMAL)
        self.assertEqual(response.details, {"arg": "arg"})
        self.assertEqual(
            VALIDATIONS["simple_validation_with_action_in_yaml"]["settings"],
            {"notification": {"update_thread_interval": 3600}},
        )
        self.assertEqual(
            VALIDATIONS["simple_validation_with_action_in_yaml"]["schedule"],
            {"every": {"minutes": 1}},
        )
        mock_logger.info.assert_has_calls(
            [
                call("common action executed"),
            ]
        )

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    def test_execute_validation_with_action_defined_from_yaml_when_error(self):
        load_validations()
        response = VALIDATIONS["simple_validation_with_error_in_yaml"]["ref"]()
        self.assertEqual(response.status, PROBLEM)

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
        result = VALIDATIONS["simple_with_invalid_action_validation"]["ref"]()
        mock_logger.error.assert_called_with(
            "validation error %s: %s",
            "simple_with_invalid_action_validation",
            "invalid_action() takes 0 positional arguments but 2 were given",
            extra={"traceback": "traceback"},
        )
        self.assertEqual(result.status, PROBLEM)

    @patch("lifeguard.validations.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.validations.logger")
    @patch("lifeguard.validations.traceback")
    def test_execute_validation_with_error_and_error_actions(
        self, mock_traceback, mock_logger
    ):
        mock_traceback.format_exc.return_value = "traceback"
        load_validations()
        VALIDATIONS["simple_validation_with_action_on_errors"]["ref"]()

        response = ON_ERROR_ACTION_MOCK.mock_calls[0][1][0]
        settings = ON_ERROR_ACTION_MOCK.mock_calls[0][1][1]

        self.assertEqual(
            response.validation_name, "simple_validation_with_action_on_errors"
        )
        self.assertEqual(
            response.details,
            {
                "exception": "error",
                "traceback": "traceback",
                "use_error_template": True,
            },
        )
        self.assertEqual(response.status, "PROBLEM")
        self.assertEqual(settings, {})
