"""
Lifeguard validation core
"""

import os
import sys
import traceback
from functools import wraps

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY

VERSION = VERSION = "0.0.1"

NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]

VALIDATIONS = {}


class ValidationResponse:
    def __init__(self, validation_name, status, details, settings=None):
        self.validation_name = validation_name
        self.status = status
        self.details = details
        self.settings = settings

    def __str__(self):
        return str(
            {
                "validation_name": self.validation_name,
                "status": self.status,
                "details": self.details,
                "settings": self.settings,
            }
        )


def change_status(old, new):
    if ACTION_STATUSES.index(new) > ACTION_STATUSES.index(old):
        return new
    return old


def load_validations():
    sys.path.append(LIFEGUARD_DIRECTORY)
    for f in os.listdir(os.path.join(LIFEGUARD_DIRECTORY, "validations")):
        if f.endswith("_validation.py"):
            validation = f.replace(".py", "")

            logger.info("loading validation {}".format(validation))

            module = "validations.%s" % (validation)
            if module not in sys.modules:
                __import__(module)


def validation(description=None, actions=None, schedule=None):
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
                        str(action.__name__),
                        str(result),
                    )
                    action(result)

                return result
            except Exception as exception:
                logger.warning(
                    "validation error %s: %s",
                    str(decorated.__name__),
                    str(exception),
                    extra={"traceback": traceback.format_exc()},
                )

        VALIDATIONS[decorated.__name__] = {
            "ref": wrapped,
            "description": description,
            "actions": actions,
            "schedule": schedule,
        }

        return wrapped

    return function_reference
