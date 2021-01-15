import os
import sys
from flask import Blueprint
from functools import wraps

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY

custom_controllers = Blueprint("custom", __name__)


def register_custom_controller(path, function, options):
    endpoint = options.pop("endpoint", function.__name__)
    custom_controllers.add_url_rule(path, endpoint, function, **options)


def load_custom_controllers():
    """
    Load custom controllers from application path
    """

    sys.path.append(LIFEGUARD_DIRECTORY)

    if not os.path.exists(os.path.join(LIFEGUARD_DIRECTORY, "controllers")):
        return

    for controller_file in os.listdir(os.path.join(LIFEGUARD_DIRECTORY, "controllers")):
        if controller_file.endswith("_controller.py"):
            controller_module_name = controller_file.replace(".py", "")
            logger.info("loading custom controller %s", controller_module_name)

            module = "controllers.%s" % (controller_module_name)
            if module not in sys.modules:
                __import__(module)


def controller(path, **options):
    """
    Decorator to configure a custom controller
    """

    def function_reference(decorated):
        @wraps(decorated)
        def wrapped(*args, **kwargs):
            return decorated(*args, **kwargs)

        register_custom_controller(path, decorated, options)

        return wrapped

    return function_reference
