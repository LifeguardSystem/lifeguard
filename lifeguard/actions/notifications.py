"""
Base of action used to notification
"""
import json

from lifeguard import NORMAL, PROBLEM
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.notifications import NOTIFICATION_METHODS, NotificationStatus
from lifeguard.repositories import NotificationRepository


def notify_in_thread(validation_response, settings):
    """
    Create a new thread to notify problem status.
    When status returns to NORMAL thread should be closed.

    :param validation_response: a validation response
    :param settings: validation settings
    """
    repository = NotificationRepository()
    last_notification_status = repository.fetch_last_notification_for_a_validation(
        validation_response.validation_name
    )

    if not last_notification_status and validation_response.status != PROBLEM:
        return

    content = json.dumps(validation_response.details)

    if not last_notification_status:
        thread_ids = {}
        for notification_method in NOTIFICATION_METHODS:
            thread_ids[notification_method.name] = notification_method.init_thread(
                content, settings
            )

        last_notification_status = NotificationStatus(
            validation_response.validation_name, thread_ids
        )
    else:
        for notification_method in NOTIFICATION_METHODS:
            if notification_method.name in last_notification_status.thread_ids:
                __send_notification_in_thread(
                    last_notification_status,
                    notification_method,
                    content,
                    settings,
                    validation_response,
                )
    repository.save_last_notification_for_a_validation(last_notification_status)


def __send_notification_in_thread(
    last_notification_status,
    notification_method,
    content,
    settings,
    validation_response,
):
    thread_id = last_notification_status.thread_ids[notification_method.name]
    if validation_response.status == NORMAL:
        notification_method.close_thread(thread_id, content, settings)
        last_notification_status.close()
    else:
        notification_method.update_thread(thread_id, content, settings)
        last_notification_status.update()


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

    response_settings = validation_response.settings or {}
    notification_settings = response_settings.get("notification", {})
    should_notify = notification_settings.get("notify", False)

    if should_notify:
        content = json.dumps(validation_response.details)
        for notification_method in NOTIFICATION_METHODS:
            notification_method.send_single_message(content, settings)
