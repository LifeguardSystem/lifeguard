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

    if not implementation:
        return

    if repository in IMPLEMENTATIONS:
        logger.warning("overwriting implementation for respository %s", repository)
    logger.info(
        "loading implementation %s for repository %s", implementation, repository,
    )
    IMPLEMENTATIONS[repository] = load_implementation(implementation)


def load_implementation(implementation):
    package_path = implementation.split(".")
    class_name = package_path.pop(-1)
    return getattr(__import__(".".join(package_path)), class_name)()
