"""
Base of notification system
"""

from datetime import datetime
from json import JSONEncoder

from lifeguard.logger import lifeguard_logger as logger

NOTIFICATION_METHODS = []


class NotificationStatus:
    """
    Notification status class
    """

    def __init__(self, validation_name, thread_ids, options=None):
        self._validation_name = validation_name
        self._thread_ids = thread_ids
        self._options = options
        self._opened = True
        self._last_notification = datetime.now()

    @property
    def validation_name(self):
        """
        Return validation name
        """
        return self._validation_name

    @property
    def thread_ids(self):
        """
        Return thread ids
        """
        return self._thread_ids

    @property
    def is_opened(self):
        """
        Return opened
        """
        return self._opened

    @is_opened.setter
    def is_opened(self, value):
        self._opened = value

    def update(self):
        """
        Close notification
        """
        self._last_notification = datetime.now()

    def close(self):
        """
        Close notification
        """
        self._last_notification = datetime.now()
        self._opened = False

    @property
    def options(self):
        """
        Return options
        """
        return self._options

    @property
    def last_notification(self):
        """
        Return last notification
        """
        return self._last_notification

    @last_notification.setter
    def last_notification(self, value):
        """
        Setter for last notification
        """
        self._last_notification = value

    def get_attributes(self):
        """
        Return all attributes in a dict.
        """
        attributes = {
            "validation_name": self.validation_name,
            "thread_ids": self.thread_ids,
            "options": self.options,
            "is_opened": self.is_opened,
        }

        if self.last_notification:
            attributes["last_notification"] = self.last_notification.strftime(
                "%Y-%m-%dT%H:%M"
            )
        return attributes

    def __str__(self):
        return str(self.get_attributes())


class ValidationResponseEncoder(JSONEncoder):
    """
    Enconder for Validation Response
    """

    def default(self, validation_response):
        """
        Default implementation for validation response encoder
        """

        return validation_response.get_attributes()


class NotificationBase:
    """
    Base of notification
    """

    @property
    def name(self):
        """
        Implementation name
        """
        return "not implemented"

    def send_single_message(self, content, settings):
        """
        Notify in single message
        """

    def init_thread(self, content, settings):
        """
        Notify in single message

        :return: str
        """

    def update_thread(self, thread_id, content, settings):
        """
        Update thread with a new message
        """

    def close_thread(self, thread_id, content, settings):
        """
        Close thread with a final message
        """


def append_notification_implementation(implementation):
    """
    Append a new implementation
    """
    if implementation.__name__ not in [
        notification_method.__class__.__name__
        for notification_method in NOTIFICATION_METHODS
    ]:
        logger.info("appending implementation %s", implementation.__name__)
        NOTIFICATION_METHODS.append(implementation())
