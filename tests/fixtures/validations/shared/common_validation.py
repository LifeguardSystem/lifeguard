from lifeguard import NORMAL
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.validations import ValidationResponse


def common_action(_response, _settings):
    logger.info("common action executed")


def common_validation(arg):
    return ValidationResponse(NORMAL, {"arg": arg})
