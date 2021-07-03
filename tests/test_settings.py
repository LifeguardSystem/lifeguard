import unittest

from unittest.mock import patch, call

from lifeguard.settings import (
    LIFEGUARD_SERVER_PORT,
    LIFEGUARD_DIRECTORY,
    LIFEGUARD_RUN_ONLY_VALIDATIONS,
    LOG_LEVEL,
    SETTINGS_MANAGER,
    SettingsManager,
    AttributeNotFoundInSettings,
)


class SettingsTest(unittest.TestCase):
    def test_server_port(self):
        self.assertEqual(LIFEGUARD_SERVER_PORT, "5567")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_SERVER_PORT"]["description"],
            "Lifeguard server port number",
        )

    def test_log_level(self):
        self.assertEqual(LOG_LEVEL, "INFO")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_LOG_LEVEL"]["description"],
            "Sets the Lifeguard's core log level",
        )

    def test_lifeguard_directory(self):
        self.assertEqual(LIFEGUARD_DIRECTORY, ".")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_DIRECTORY"]["description"],
            "Location of validations and others resources",
        )

    def test_lifeguard_run_only_validations_default(self):
        self.assertEqual(LIFEGUARD_RUN_ONLY_VALIDATIONS, [])
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_RUN_ONLY_VALIDATIONS"]["description"],
            "A comma separated list with validations name to be run",
        )

    def test_get_default_value_for_dynamic_attribute(self):
        settings = SettingsManager(
            {
                r"DYNAMIC_\w+_ATTRIBUTE": {
                    "default": "default_value",
                    "description": "dynammic descritpion",
                }
            }
        )

        self.assertEqual(settings.read_value("DYNAMIC_TEST_ATTRIBUTE"), "default_value")

    @patch("lifeguard.settings.environ")
    def test_get_value_for_dynamic_attribute_from_env(self, mock_environ):
        mock_environ.get.return_value = "from env"
        settings = SettingsManager(
            {
                r"DYNAMIC_\w+_ATTRIBUTE": {
                    "default": "default_value",
                    "description": "dynammic descritpion",
                }
            }
        )
        self.assertEqual(settings.read_value("DYNAMIC_TEST_ATTRIBUTE"), "from env")
        mock_environ.get.assert_has_calls(
            [
                call("DYNAMIC_\\w+_ATTRIBUTE", "default_value"),
                call("DYNAMIC_TEST_ATTRIBUTE", "default_value"),
            ]
        )

    def test_raise_exception_if_pattern_not_found(self):
        settings = SettingsManager(
            {
                r"DYNAMIC_\w+_ATTRIBUTE": {
                    "default": "default_value",
                    "description": "dynammic descritpion",
                }
            }
        )
        with self.assertRaises(AttributeNotFoundInSettings):
            settings.read_value("DYNAMIC__ATTRIBUTE")
