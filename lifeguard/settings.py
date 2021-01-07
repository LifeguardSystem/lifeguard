"""
Lifeguard core settings
"""
import sys
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
        "LIFEGUARD_SERVER_PORT": {
            "default": "5567",
            "description": "Lifeguard server port number",
        },
        "LIFEGUARD_DIRECTORY": {
            "default": "/data/lifeguard",
            "description": "Location of validations and others resources",
        },
        "LIFEGUARD_LOG_LEVEL": {
            "default": "INFO",
            "description": "Sets the Lifeguard's core log level",
        },
        "LIFEGUARD_HTTP_PROXY": {
            "default": None,
            "description": "Proxy used to http calls",
        },
        "LIFEGUARD_HTTPS_PROXY": {
            "default": None,
            "description": "Proxy used to https calls",
        },
    }
)

LIFEGUARD_SERVER_PORT = SETTINGS_MANAGER.read_value("LIFEGUARD_SERVER_PORT")
LIFEGUARD_DIRECTORY = SETTINGS_MANAGER.read_value("LIFEGUARD_DIRECTORY")
LOG_LEVEL = SETTINGS_MANAGER.read_value("LIFEGUARD_LOG_LEVEL")
HTTP_PROXY = SETTINGS_MANAGER.read_value("LIFEGUARD_HTTP_PROXY")
HTTPS_PROXY = SETTINGS_MANAGER.read_value("LIFEGUARD_HTTPS_PROXY")
