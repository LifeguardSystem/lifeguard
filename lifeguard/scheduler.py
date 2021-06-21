import time
import traceback
import schedule
import threading

from lifeguard.validations import VALIDATIONS
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_THREAD_ENABLE

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


def run_threaded(job_func):
    threading.Thread(target=job_func).start()


def configure_validations():
    for validation in VALIDATIONS:
        content = VALIDATIONS[validation]
        if "every" in content["schedule"]:
            time_period = get_time_period(content)
            if time_period in valid_time_periods:
                job_instance = schedule.every(
                    content["schedule"]["every"][time_period])
                job_func = get_dynamic_job_func(job_instance, time_period)
                if LIFEGUARD_THREAD_ENABLE == "true":
                    job_func.do(run_threaded, content["ref"])
                else:
                    job_func.do(content["ref"])


def get_dynamic_job_func(job_instance, time_period):
    return getattr(job_instance, time_period)


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
