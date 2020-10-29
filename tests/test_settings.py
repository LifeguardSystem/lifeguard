import unittest


from lifeguard.settings import LOG_LEVEL, SETTINGS_MANAGER


class SettingsTest(unittest.TestCase):
    def test_log_level(self):

        self.assertEqual(LOG_LEVEL, "INFO")
        self.assertEqual(
            SETTINGS_MANAGER.settings["LOG_LEVEL"]["description"],
            "Sets the Lifeguard's core log level",
        )
