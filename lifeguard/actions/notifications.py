"""
Base of action used to notification
"""
from datetime import datetime
import jinja2
import json

from lifeguard import NORMAL, PROBLEM
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.notifications import (
    NOTIFICATION_METHODS,
    INIT_THREAD_MESSAGE_NOTIFICATION,
    CLOSE_THREAD_MESSAGE_NOTIFICATION,
    SINGLE_MESSAGE_NOTIFICATION,
    UPDATE_THREAD_MESSAGE_NOTIFICATION,
    NotificationOccurrence,
    NotificationStatus,
)
from lifeguard.repositories import HistoryRepository, NotificationRepository
from lifeguard.settings import LIFEGUARD_APPEND_NOTIFICATION_TO_HISTORY


def __get_content(validation_response, settings):
    if "template" in settings.get("notification", {}):
        template = jinja2.Template(settings["notification"]["template"])
        if isinstance(validation_response.settings["notification"]["data"], list):
            return [
                template.render(**data)
                for data in validation_response.settings["notification"]["data"]
            ]
        return template.render(**validation_response.settings["notification"]["data"])
    return json.dumps(validation_response.details)


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

    content = __get_content(validation_response, settings)

    if not last_notification_status:
        thread_ids = {}
        for notification_method in NOTIFICATION_METHODS:
            thread_ids[notification_method.name] = notification_method.init_thread(
                content, settings
            )

        last_notification_status = NotificationStatus(
            validation_response.validation_name, thread_ids
        )
        __append_notification(
            validation_response,
            settings,
            INIT_THREAD_MESSAGE_NOTIFICATION,
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
        __append_notification(
            validation_response,
            settings,
            CLOSE_THREAD_MESSAGE_NOTIFICATION,
        )
    else:
        last_notification_was_in_seconds = (
            datetime.now() - last_notification_status.last_notification
        ).seconds
        interval = settings.get("notification", {}).get("update_thread_interval", 0)

        if last_notification_was_in_seconds >= interval:
            logger.debug("updating notification")
            notification_method.update_thread(thread_id, content, settings)
            last_notification_status.update()
            __append_notification(
                validation_response,
                settings,
                UPDATE_THREAD_MESSAGE_NOTIFICATION,
            )


def __append_notification(validation_response, settings, notification_type):
    notification_settings = settings.get("notification", {})
    add_to_history = notification_settings.get(
        "add_to_history", LIFEGUARD_APPEND_NOTIFICATION_TO_HISTORY
    )
    if add_to_history:
        HistoryRepository().append_notification(
            NotificationOccurrence(
                validation_name=validation_response.validation_name,
                details=validation_response.details,
                status=validation_response.status,
                notification_type=notification_type,
            )
        )


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
        content = __get_content(validation_response, settings)
        for notification_method in NOTIFICATION_METHODS:
            notification_method.send_single_message(content, settings)

        __append_notification(
            validation_response, settings, SINGLE_MESSAGE_NOTIFICATION
        )
