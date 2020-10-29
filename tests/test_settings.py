import unittest


from lifeguard.settings import LOG_LEVEL, SETTINGS_MANAGER, LIFEGUARD_DIRECTORY


class SettingsTest(unittest.TestCase):
    def test_log_level(self):
        self.assertEqual(LOG_LEVEL, "INFO")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LOG_LEVEL"]["description"],
            "Sets the Lifeguard's core log level",
        )

    def test_lifeguard_directory(self):
        self.assertEqual(LIFEGUARD_DIRECTORY, "/data/lifeguard")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LIFEGUARD_DIRECTORY"]["description"],
            "Location of validations and others resources",
        )
