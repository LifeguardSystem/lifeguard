import time
import traceback
import schedule

from lifeguard.validations import VALIDATIONS
from lifeguard.logger import lifeguard_logger as logger

valid_time_periods = [
    "seconds",
    "minutes",
    "hours",
    "days",
    "weeks",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def configure_validations():
    for validation in VALIDATIONS:
        content = VALIDATIONS[validation]
        if "every" in content["schedule"]:
            time_period = get_time_period(content)
            if time_period in valid_time_periods:
                schedule.every(content["schedule"]["every"][time_period])[
                    time_period
                ].do(content["ref"])


def get_time_period(content):
    keys = content["schedule"]["every"].keys()
    time_period = list(keys)[0]
    return time_period


def start_scheduler():
    configure_validations()
    while True:
        time.sleep(1)
        try:
            schedule.run_pending()
        except Exception as exception:
            logger.error(
                "error on execute scheduler %s",
                str(exception),
                extra={"traceback": traceback.format_exc()},
            )
