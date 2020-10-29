"""
Lifeguard core settings
"""
from os import environ


class SettingsManager(object):
    def __init__(self, settings):
        self.settings = settings

        for entry in self.settings:
            setattr(self, "__{}".format(entry.lower()), self.__get_value(entry))

    def __get_value(self, name):
        options = self.settings[name]
        return environ.get(name, options["default"])

    def read_value(self, name):
        return getattr(self, "__{}".format(name.lower()))


SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_DIRECTORY": {
            "default": "/data/lifeguard",
            "description": "Location of validations and others resources",
        },
        "LOG_LEVEL": {
            "default": "INFO",
            "description": "Sets the Lifeguard's core log level",
        },
    }
)

LIFEGUARD_DIRECTORY = SETTINGS_MANAGER.read_value("LIFEGUARD_DIRECTORY")
LOG_LEVEL = SETTINGS_MANAGER.read_value("LOG_LEVEL")
