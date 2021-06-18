"""
Lifeguard validation core
"""
import importlib
import os
import sys

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.repositories import declare_implementation
from lifeguard.settings import LIFEGUARD_DIRECTORY, SETTINGS_MANAGER
from lifeguard.controllers import load_custom_controllers
from lifeguard.validations import load_validations

NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]


def change_status(old, new):
    """
    Change status by severity
    """
    if ACTION_STATUSES.index(new) > ACTION_STATUSES.index(old):
        return new
    return old


def recover_settings():
    """
    Get settings.py from root of project
    """

    logger.info("lifeguard directory %s", LIFEGUARD_DIRECTORY)
    sys.path.append(LIFEGUARD_DIRECTORY)

    logger.info("path: %s", sys.path)

    lifeguard_settings = "lifeguard_settings"
    logger.info("loading %s", lifeguard_settings)
    if importlib.util.find_spec(lifeguard_settings) is None:
        logger.error("lifeguard_settings.py not found!!!")
        sys.exit(-1)
    return __import__(lifeguard_settings)


def setup(lifeguard_context):
    """
    Setup lifeguard context
    """
    # init plugins
    lifeguard_settings = recover_settings()

    for plugin in lifeguard_settings.PLUGINS:
        SETTINGS_MANAGER.settings.update(plugin.settings.SETTINGS_MANAGER.settings)
        if not lifeguard_context.only_settings:
            plugin.init(lifeguard_context)

    load_custom_controllers()
    load_validations()

    lifeguard_settings.setup(lifeguard_context)
