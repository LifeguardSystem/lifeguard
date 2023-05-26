import os
import sys
import traceback
from json import JSONEncoder
from functools import wraps

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import (
    LIFEGUARD_DIRECTORY,
    LIFEGUARD_RUN_ONLY_VALIDATIONS,
    LIFEGUARD_SKIP_VALIDATIONS,
)
from lifeguard.statuses import PROBLEM, ACTION_STATUSES
from lifeguard.utils import build_import

VALIDATIONS = {}


def __execute_actions(actions, result, settings):
    for action in actions or []:
        logger.info(
            "executing action %s with result %s...",
            str(action.__name__),
            str(result),
        )
        action(result, settings)


class ValidationResponse:
    """
    Represents the result of a validation
    """

    def __init__(
        self, status, details, settings=None, last_execution=None, validation_name=None
    ):
        self._status = self.__validate_status(status)
        self._details = details
        self._settings = settings
        self._last_execution = last_execution
        self._validation_name = validation_name

    @property
    def validation_name(self):
        """
        Return validation name
        """
        return self._validation_name

    @property
    def status(self):
        """
        Return status
        """
        return self._status

    @property
    def details(self):
        """
        Return details
        """
        return self._details

    @property
    def settings(self):
        """
        Return settings
        """
        return self._settings

    @property
    def last_execution(self):
        """
        Return last execution
        """
        return self._last_execution

    @validation_name.setter
    def validation_name(self, value):
        """
        Setter for validation name
        """
        self._validation_name = value

    @last_execution.setter
    def last_execution(self, value):
        """
        Setter for last execution
        """
        self._last_execution = value

    def get_attributes(self):
        """
        Return all attributes in a dict.
        """
        attributes = {
            "validation_name": self.validation_name,
            "status": self.status,
            "details": self.details,
            "settings": self.settings,
        }

        if self.last_execution:
            attributes["last_execution"] = self.last_execution.strftime(
                "%Y-%m-%dT%H:%M"
            )
        return attributes

    def __str__(self):
        return str(self.get_attributes())

    def __validate_status(self, status):
        if status not in ACTION_STATUSES:
            raise ValueError(f"{status} is not a valid status")
        return status


class ValidationResponseEncoder(JSONEncoder):
    """
    Enconder for Validation Response
    """

    def default(self, validation_response):
        """
        Default implementation for validation response encoder
        """

        return validation_response.get_attributes()


def load_validations():
    """
    Load validations from application path
    """
    for root, _dirs, files in os.walk(os.path.join(LIFEGUARD_DIRECTORY, "validations")):
        root = os.path.relpath(root, os.path.join(LIFEGUARD_DIRECTORY))
        for validation_file in files:
            if validation_file.endswith("_validation.py"):
                validation_module_name = (
                    f'{build_import(root, validation_file.replace(".py", ""))}'
                )
                logger.info("loading validation %s", validation_file.replace(".py", ""))

                module = "%s" % (validation_module_name)
                if module not in sys.modules:
                    __import__(module)


def validation(
    description=None, actions=None, schedule=None, settings=None, actions_on_error=None
):
    """
    Decorator to configure a validation
    """
    if not settings:
        settings = {}

    def function_reference(decorated):
        @wraps(decorated)
        def wrapped(*args, **kwargs):
            try:
                if LIFEGUARD_RUN_ONLY_VALIDATIONS and (
                    decorated.__name__ not in LIFEGUARD_RUN_ONLY_VALIDATIONS
                ):
                    logger.info(
                        "validation %s not in LIFEGUARD_RUN_ONLY_VALIDATIONS",
                        decorated.__name__,
                    )
                    return None

                if LIFEGUARD_SKIP_VALIDATIONS and (
                    decorated.__name__ in LIFEGUARD_SKIP_VALIDATIONS
                ):
                    logger.info(
                        "validation %s in LIFEGUARD_SKIP_VALIDATIONS",
                        decorated.__name__,
                    )
                    return None

                result = decorated(*args, **kwargs)
                result.validation_name = decorated.__name__
                __execute_actions(actions, result, settings)

                return result
            except Exception as exception:
                logger.error(
                    "validation error %s: %s",
                    str(decorated.__name__),
                    str(exception),
                    extra={"traceback": traceback.format_exc()},
                )
                __execute_actions(
                    actions_on_error,
                    ValidationResponse(
                        PROBLEM,
                        {
                            "exception": str(exception),
                            "traceback": traceback.format_exc(),
                            "use_error_template": True,
                        },
                        validation_name=decorated.__name__,
                    ),
                    settings,
                )

        VALIDATIONS[decorated.__name__] = {
            "ref": wrapped,
            "description": description,
            "actions": actions,
            "schedule": schedule,
            "settings": settings,
        }

        return wrapped

    return function_reference
