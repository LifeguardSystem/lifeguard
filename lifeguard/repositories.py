"""
Interface repositories
"""
from lifeguard.logger import lifeguard_logger as logger

IMPLEMENTATIONS = {}


class BaseRepository(object):
    def __init_repository__(self, repository):
        self.__implementation__ = IMPLEMENTATIONS[repository]


class ValidationRepository(BaseRepository):
    def __init__(self):
        BaseRepository.__init_repository__(self, "validation")

    def save_validation_result(self, validation_result):
        self.__implementation__.save_validation_result(validation_result)

    def fetch_last_validation_result(self, validation_name):
        self.__implementation__.fetch_last_validation_result(validation_name)


def declare_implementation(repository, implementation):
    if repository in IMPLEMENTATIONS:
        logger.warning("overwriting implementation for respository %s", repository)
    IMPLEMENTATIONS[repository] = implementation
