"""
Base of action used to notification
"""
import json

from lifeguard.helpers import load_implementation
from lifeguard.settings import NOTIFICATION_IMPLEMENTATIONS

NOTIFICATION_METHODS = []


def notify_in_thread(validation_response, settings):
    """
    Create a new thread to notify problem status.
    When status returns to NORMAL thread should be closed.

    :param validation_response: a validation response
    :param settings: validation settings
    """

    pass


def notify_in_single_message(validation_response, settings):
    """
    This action sends single message on a new thread.

    To send notification validation response should have:
    {
        "notification": {"notify": True}
    }

    :param validation_response: a validation response
    :param settings: validation settings
    """

    if not NOTIFICATION_METHODS:
        __build_notification_methods()

    response_settings = validation_response.settings or {}
    notification_settings = response_settings.get("notification", {})
    should_notify = notification_settings.get("notify", False)

    if should_notify:
        content = json.dumps(validation_response.details)
        for notification_method in NOTIFICATION_METHODS:
            notification_method.send_single_message(content, settings)


def __build_notification_methods():
    for imp in NOTIFICATION_IMPLEMENTATIONS.split(","):
        NOTIFICATION_METHODS.append(load_implementation(imp))
