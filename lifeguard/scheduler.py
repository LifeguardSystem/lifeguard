import time
import traceback
import schedule

from lifeguard.validations import VALIDATIONS
from lifeguard.logger import lifeguard_logger as logger


def configure_validations():
    for validation in VALIDATIONS:
        content = VALIDATIONS[validation]
        if "every" in content["schedule"]:
            if "minutes" in content["schedule"]["every"]:
                schedule.every(content["schedule"]["every"]["minutes"]).minutes.do(
                    content["ref"]
                )


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
