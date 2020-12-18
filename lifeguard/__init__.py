"""
Lifeguard validation core
"""
from lifeguard.repositories import declare_implementation
from lifeguard.validations import load_validations
from lifeguard.settings import (
    VALIDATION_REPOSITORY_IMPLEMENTATION,
    NOTIFICATION_REPOSITORY_IMPLEMENTATION,
)

VERSION = "0.0.6"

NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]


def change_status(old, new):
    if ACTION_STATUSES.index(new) > ACTION_STATUSES.index(old):
        return new
    return old


def setup():
    load_validations()
    declare_implementation("validation", VALIDATION_REPOSITORY_IMPLEMENTATION)
    declare_implementation("notification", NOTIFICATION_REPOSITORY_IMPLEMENTATION)
