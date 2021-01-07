"""
Lifeguard validation core
"""
import os
import sys

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.repositories import declare_implementation
from lifeguard.settings import LIFEGUARD_DIRECTORY
from lifeguard.validations import load_validations

VERSION = "0.0.7"

NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]
LIFEGUARD_CONTEXT = {}

sys.path.append(LIFEGUARD_DIRECTORY)


class LifeguardContext:
    """
    Lifeguard Context
    """


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

    lifeguard_settings = "lifeguard_settings"
    logger.info("loading %s", lifeguard_settings)
    return __import__(lifeguard_settings)


def setup():
    """
    Setup lifeguard context
    """
    lifeguard_context = LifeguardContext()

    # init plugins
    lifeguard_settings = recover_settings()

    for plugin in lifeguard_settings.PLUGINS:
        plugin.init(lifeguard_context)

    load_validations()

    lifeguard_settings.setup(lifeguard_context)
