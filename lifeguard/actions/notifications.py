"""
Base of action used to notification
"""
from copy import deepcopy
from datetime import datetime
import jinja2
import json

from lifeguard.statuses import NORMAL, PROBLEM
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


def __merge_details_and_data(validation_response, notification_data):
    data = deepcopy(validation_response.details)
    data.update(notification_data)
    return data


def __get_content(validation_response, settings):
    template_origin = (
        "template"
        if not (validation_response.details or {}).get("use_error_template", False)
        else "template_error"
    )

    if template_origin in settings.get("notification", {}):
        template = jinja2.Template(settings["notification"][template_origin])
        notification_data = (
            (validation_response.settings or {}).get("notification", {}).get("data", {})
        )
        if isinstance(notification_data, list):
            return [
                template.render(**__merge_details_and_data(validation_response, data))
                for data in notification_data
            ]
        return template.render(
            **__merge_details_and_data(
                validation_response,
                notification_data,
            )
        )
    return json.dumps(validation_response.details)


def __get_notification_methods(settings):
    disabled = settings.get("notification", {}).get("disabled", [])
    return [method for method in NOTIFICATION_METHODS if method.name not in disabled]


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
        for notification_method in __get_notification_methods(settings):
            thread_ids[notification_method.name] = notification_method.init_thread(
                deepcopy(content), settings
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
        for notification_method in __get_notification_methods(settings):
            if notification_method.name in last_notification_status.thread_ids:
                __send_notification_in_thread(
                    last_notification_status,
                    notification_method,
                    deepcopy(content),
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
        for notification_method in __get_notification_methods(settings):
            notification_method.send_single_message(deepcopy(content), settings)

        __append_notification(
            validation_response, settings, SINGLE_MESSAGE_NOTIFICATION
        )
