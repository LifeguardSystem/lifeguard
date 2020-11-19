import unittest
import sys

from lifeguard.settings import (
    LIFEGUARD_DIRECTORY,
    LOG_LEVEL,
    SETTINGS_MANAGER,
    VALIDATION_REPOSITORY_IMPLEMENTATION,
)


class SettingsTest(unittest.TestCase):
    def test_log_level(self):
        self.assertEqual(LOG_LEVEL, "INFO")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_LOG_LEVEL"]["description"],
            "Sets the Lifeguard's core log level",
        )

    def test_lifeguard_directory(self):
        self.assertEqual(LIFEGUARD_DIRECTORY, "/data/lifeguard")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_DIRECTORY"]["description"],
            "Location of validations and others resources",
        )

    def test_lifeguard_repository_implementation(self):
        self.assertEqual(VALIDATION_REPOSITORY_IMPLEMENTATION, None)
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_VALIDATION_REPOSITORY_IMPLEMENTATION"][
                "description"
            ],
            "Full package path to validation implementation class",
        )

    def test_lifeguard_repository_implementation_load_module(self):
        sys.path.append("tests/fixtures")
        SETTINGS_MANAGER.settings["LIFEGUARD_VALIDATION_REPOSITORY_IMPLEMENTATION"][
            "default"
        ] = "fixtures_repositories.TestValidationRepository"
        result = SETTINGS_MANAGER.load_class(
            "LIFEGUARD_VALIDATION_REPOSITORY_IMPLEMENTATION"
        )
        self.assertEqual(result.__name__, "TestValidationRepository")
