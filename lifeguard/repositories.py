"""
Interface repositories
"""
from datetime import datetime

from lifeguard.logger import lifeguard_logger as logger

IMPLEMENTATIONS = {}


class BaseRepository(object):
    def __init_repository__(self, repository):
        self.__implementation__ = IMPLEMENTATIONS[repository]


class ValidationRepository(BaseRepository):
    def __init__(self):
        BaseRepository.__init_repository__(self, "validation")

    def save_validation_result(self, validation_result):
        validation_result.last_execution = datetime.now()
        self.__implementation__.save_validation_result(validation_result)

    def fetch_last_validation_result(self, validation_name):
        return self.__implementation__.fetch_last_validation_result(validation_name)

    def fetch_all_validation_results(self):
        return self.__implementation__.fetch_all_validation_results()


class NotificationRepository(BaseRepository):
    def __init__(self):
        BaseRepository.__init_repository__(self, "notification")

    def save_last_notification_for_a_validation(self, notification):
        self.__implementation__.save_last_notification_for_a_validation(notification)

    def fetch_last_notification_for_a_validation(self, validation_name):
        return self.__implementation__.fetch_last_notification_for_a_validation(
            validation_name
        )


class HistoryRepository(BaseRepository):
    def __init__(self):
        BaseRepository.__init_repository__(self, "history")

    def append_notification(self, notification_occurrence):
        self.__implementation__.append_notification(notification_occurrence)

    def fetch_notifications(
        self, start_interval, end_interval, filters={}, page=None, limit=None
    ):
        return self.__implementation__.fetch_notifications(
            start_interval, end_interval, filters, page, limit
        )

    def count_notifications(self, start_interval=None, end_interval=None, filters={}):
        return self.__implementation__.count_notifications(
            start_interval, end_interval, filters
        )


def declare_implementation(repository, implementation):

    if repository in IMPLEMENTATIONS:
        logger.warning("overwriting implementation for respository %s", repository)
    logger.info(
        "loading implementation %s for repository %s",
        implementation.__name__,
        repository,
    )
    IMPLEMENTATIONS[repository] = implementation()
