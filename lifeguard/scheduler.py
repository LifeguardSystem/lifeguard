import time
import traceback

import schedule

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.validations import VALIDATIONS

VALID_TIME_PERIODS = [
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

MOMENTS = [
    "second",
    "minute",
    "hour",
    "day",
    "week",
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
            if time_period in VALID_TIME_PERIODS:
                job_instance = schedule.every(content["schedule"]["every"][time_period])
                job_func = get_dynamic_job_func(job_instance, time_period)
                job_func.do(content["ref"])
        if "at" in content["schedule"]:
            time_moment = get_time_moment(content)
            if time_moment in MOMENTS:
                moment = getattr(schedule.every(), time_moment)
                moment.at(content["schedule"]["at"][time_moment]).do(content["ref"])


def get_dynamic_job_func(job_instance, time_period):
    return getattr(job_instance, time_period)


def get_time_period(content):
    keys = content["schedule"]["every"].keys()
    time_period = list(keys)[0]
    return time_period


def get_time_moment(content):
    keys = content["schedule"]["at"].keys()
    time_moment = list(keys)[0]
    return time_moment


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
