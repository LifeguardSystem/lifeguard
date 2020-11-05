import os
import sys
import traceback
from json import JSONEncoder
from functools import wraps

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY

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


class ValidationResponseEncoder(JSONEncoder):
    def default(self, validation_response):
        return validation_response.__dict__


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
