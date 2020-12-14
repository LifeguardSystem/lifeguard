"""
Base of notification system
"""


class NotificationStatus(object):
    """
    Notification status class
    """

    def __init__(self, validation_name, options=None):
        self.validation_name = validation_name
        self.options = options


class NotificationBase(object):
    """
    Base of notification
    """

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

    def close_thread(self, content, settings):
        """
        Close thread with a final message
        """
