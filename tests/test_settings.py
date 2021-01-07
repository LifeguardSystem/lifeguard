import unittest

from lifeguard.settings import (
    LIFEGUARD_SERVER_PORT,
    LIFEGUARD_DIRECTORY,
    LOG_LEVEL,
    SETTINGS_MANAGER,
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
        self.assertEqual(LIFEGUARD_DIRECTORY, "/data/lifeguard")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_DIRECTORY"]["description"],
            "Location of validations and others resources",
        )
