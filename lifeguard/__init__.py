"""
Lifeguard health utils
"""

import traceback
from functools import wraps

from lifeguard.logger import lifeguard_logger as logger

VERSION = VERSION = "0.0.1"

NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]


class HealthResponse:
    def __init__(self, health, status, details, settings=None):
        self.health = health
        self.status = status
        self.details = details
        self.settings = settings

    def __str__(self):
        return str(
            {
                "health": self.health,
                "status": self.status,
                "details": self.details,
                "settings": self.settings,
            }
        )


def change_status(old, new):
    if ACTION_STATUSES.index(new) > ACTION_STATUSES.index(old):
        return new
    return old


def health(description=None, actions=None):
    """
    Decorator to configure a validation
    """

    def function_reference(decorated):
        @wraps(decorated)
        def wrapped(*args, **kwargs):
            try:
                result = decorated(*args, **kwargs)

                for action in actions or []:
                    logger.info(
                        "executing action %s with result %s...",
                        str(action),
                        str(result)[0:100],
                    )
                    action(result)

                return result
            except Exception as exception:
                logger.warning(
                    "validation error %s: %s",
                    str(decorated),
                    str(exception),
                    extra={"traceback": traceback.format_exc()},
                )

        return wrapped

    return function_reference
