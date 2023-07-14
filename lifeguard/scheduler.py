import time
import traceback

from os import walk
from os.path import getmtime, join, exists

import schedule

from lifeguard.logger import lifeguard_logger as logger
from lifeguard.validations import VALIDATIONS, load_validations, clear_validations
from lifeguard.settings import LIFEGUARD_DIRECTORY

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

WATCHED_FILES = {}
FOREVER = True


def configure_validations():
    for validation in VALIDATIONS:
        content = VALIDATIONS[validation]
        if "every" in content["schedule"]:
            time_period = get_time_period(content)
            if time_period in VALID_TIME_PERIODS:
                job_instance = schedule.every(content["schedule"]["every"][time_period])
                job_func = get_dynamic_job_func(job_instance, time_period)
                job_func.do(content["ref"]).tag("validation")
        if "at" in content["schedule"]:
            time_moment = get_time_moment(content)
            if time_moment in MOMENTS:
                moment = getattr(schedule.every(), time_moment)
                moment.at(content["schedule"]["at"][time_moment]).do(
                    content["ref"]
                ).tag("validation")


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


def __load_validations_files():
    for root, _dirs, files in walk(join(LIFEGUARD_DIRECTORY, "validations")):
        for file in files:
            if file.endswith(".yaml"):
                file_path = join(root, file)
                if file_path not in WATCHED_FILES:
                    logger.info("watching file %s", file_path)
                    WATCHED_FILES[file_path] = getmtime(file_path)


def check_if_should_reload():
    changed = False
    # check new files or changed files
    for root, _dirs, files in walk(join(LIFEGUARD_DIRECTORY, "validations")):
        for file in files:
            if file.endswith(".yaml"):
                file_path = join(root, file)
                if file_path not in WATCHED_FILES:
                    logger.info("watching file %s", file_path)
                    WATCHED_FILES[file_path] = getmtime(file_path)
                    changed = True
                else:
                    last_modified = getmtime(file_path)
                    if last_modified != WATCHED_FILES[file_path]:
                        logger.info("file changed %s", file_path)
                        WATCHED_FILES[file_path] = last_modified
                        changed = True
    # check removed files
    for file_path in list(WATCHED_FILES.keys()):
        if not exists(file_path):
            logger.info("file removed %s", file_path)
            del WATCHED_FILES[file_path]
            changed = True

    if changed:
        reload_scheduler()


def __prepend_reload_job():
    schedule.every(15).seconds.do(check_if_should_reload).tag("lifeguard")


def __clear_validations_jobs():
    schedule.clear("validation")


def reload_scheduler():
    __clear_validations_jobs()
    clear_validations()
    load_validations()
    configure_validations()


def start_scheduler():
    __load_validations_files()
    __prepend_reload_job()

    configure_validations()

    while FOREVER:
        time.sleep(1)
        try:
            schedule.run_pending()
        except Exception as exception:
            logger.error(
                "error on execute scheduler %s",
                str(exception),
                extra={"traceback": traceback.format_exc()},
            )
