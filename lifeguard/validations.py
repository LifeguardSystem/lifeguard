import os
import yaml
import sys
import traceback
from os.path import join
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


def __load_function_from_module(module_name_with_function_name):
    module_path, function_name = module_name_with_function_name.rsplit(".", 1)

    function = __import__(module_path)

    module_path = module_path.split(".")
    for module in module_path[1:]:
        function = getattr(function, module)

    return getattr(function, function_name)


def __build_validation_function(command_function, args):
    def validation_function():
        command = __load_function_from_module(command_function)
        return command(args)

    return validation_function


def __build_validation_from_settings(validation_yaml_file):
    with open(validation_yaml_file) as file:
        validation_list_from_file = yaml.load(file, Loader=yaml.FullLoader)

    for validation_settings in validation_list_from_file["validations"]:
        logger.info(
            "loading validation %s from yaml file",
            validation_settings["validation_name"],
        )
        validation_settings["actions"] = [
            __load_function_from_module(action)
            for action in validation_settings["actions"]
        ]

        command_settings = validation_settings.pop("execute")

        validation_function = __build_validation_function(
            command_settings["command"], *command_settings["args"]
        )

        validation_function.__name__ = validation_settings.pop("validation_name")

        validation(**validation_settings)(validation_function)


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
        relative_path = os.path.relpath(root, os.path.join(LIFEGUARD_DIRECTORY))
        for validation_file in files:
            if validation_file.endswith("_validation.py"):
                validation_module_name = (
                    f'{build_import(relative_path, validation_file.replace(".py", ""))}'
                )
                logger.info("loading validation %s", validation_file.replace(".py", ""))

                module = "%s" % (validation_module_name)
                if module not in sys.modules:
                    __import__(module)

            if validation_file.endswith("_validation.yaml"):
                __build_validation_from_settings(join(root, validation_file))


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
                validation_response_error = ValidationResponse(
                    PROBLEM,
                    {
                        "exception": str(exception),
                        "traceback": traceback.format_exc(),
                        "use_error_template": True,
                    },
                    validation_name=decorated.__name__,
                )
                __execute_actions(
                    actions_on_error,
                    validation_response_error,
                    settings,
                )

                return validation_response_error

        VALIDATIONS[decorated.__name__] = {
            "ref": wrapped,
            "description": description,
            "actions": actions,
            "schedule": schedule,
            "settings": settings,
        }

        return wrapped

    return function_reference
