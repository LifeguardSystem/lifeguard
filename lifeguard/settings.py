"""
Lifeguard core settings
"""
import re
from os import environ


class AttributeNotFoundInSettings(Exception):
    """Raised when the entry not found in settings"""


class SettingsManager:
    """
    Settings manager
    """

    def __init__(self, settings):
        self.settings = settings

        for entry in self.settings:
            setattr(self, "__{}".format(entry.lower()), self.__get_value(entry))

    def __get_value(self, name):
        options = self.settings[name]
        return environ.get(name, options["default"])

    def __search_dynamic_attribute(self, name):
        for entry in self.settings:
            if re.match(entry, name):
                return environ.get(name, self.settings[entry]["default"])

        raise AttributeNotFoundInSettings("{} not found".format(name))

    def read_value(self, name):
        """
        Read value from settings
        """
        if hasattr(self, "__{}".format(name.lower())):
            return getattr(self, "__{}".format(name.lower()))

        return self.__search_dynamic_attribute(name)


SETTINGS_MANAGER = SettingsManager(
    {
        "LIFEGUARD_SERVER_PORT": {
            "default": "5567",
            "description": "Lifeguard server port number",
        },
        "LIFEGUARD_DIRECTORY": {
            "default": ".",
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
        "LIFEGUARD_PUBLIC_ADDRESS": {
            "default": "http://localhost:5567",
            "description": "Address to access dashboard",
        },
        "LIFEGUARD_EMAIL_SMTP_USER": {
            "default": "smtp_user",
            "description": "SMTP user used in email action",
        },
        "LIFEGUARD_EMAIL_SMTP_PASSWD": {
            "default": "smtp_passwd",
            "description": "SMTP passwd used in email action",
        },
        "LIFEGUARD_EMAIL_SMTP_SERVER": {
            "default": "smtp_server",
            "description": "SMTP server used in email action",
        },
        "LIFEGUARD_EMAIL_SMTP_PORT": {
            "default": "smtp_port",
            "description": "SMTP port used in email action",
        },
        "LIFEGUARD_RUN_ONLY_VALIDATIONS": {
            "default": "",
            "description": "A comma separated list with validations name to be run",
        },
    }
)

LIFEGUARD_SERVER_PORT = SETTINGS_MANAGER.read_value("LIFEGUARD_SERVER_PORT")
LIFEGUARD_DIRECTORY = SETTINGS_MANAGER.read_value("LIFEGUARD_DIRECTORY")
LIFEGUARD_PUBLIC_ADDRESS = SETTINGS_MANAGER.read_value("LIFEGUARD_PUBLIC_ADDRESS")
LIFEGUARD_EMAIL_SMTP_USER = SETTINGS_MANAGER.read_value("LIFEGUARD_EMAIL_SMTP_USER")
LIFEGUARD_EMAIL_SMTP_PASSWD = SETTINGS_MANAGER.read_value("LIFEGUARD_EMAIL_SMTP_PASSWD")
LIFEGUARD_EMAIL_SMTP_SERVER = SETTINGS_MANAGER.read_value("LIFEGUARD_EMAIL_SMTP_SERVER")
LIFEGUARD_EMAIL_SMTP_PORT = SETTINGS_MANAGER.read_value("LIFEGUARD_EMAIL_SMTP_PORT")


LOG_LEVEL = SETTINGS_MANAGER.read_value("LIFEGUARD_LOG_LEVEL")
HTTP_PROXY = SETTINGS_MANAGER.read_value("LIFEGUARD_HTTP_PROXY")
HTTPS_PROXY = SETTINGS_MANAGER.read_value("LIFEGUARD_HTTPS_PROXY")

_validations = SETTINGS_MANAGER.read_value("LIFEGUARD_RUN_ONLY_VALIDATIONS").split(",")

# TODO: changes this after #27 was done
LIFEGUARD_RUN_ONLY_VALIDATIONS = [
    validation for validation in _validations if validation
]
