"""
Settings for application logging
"""
import json
import logging
import sys
import time
from datetime import datetime

from lifeguard.settings import LOG_LEVEL


class CustomFormatter(logging.Formatter):
    def __init__(self):
        super(CustomFormatter, self).__init__()

    def format(self, record):
        message_object = {
            "level": record.levelname,
            "message": {
                "fileName": record.filename,
                "lineNumber": record.lineno,
                "appName": "lifeguard",
                "message": record.msg % record.args,
            },
            "metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "processName": sys.argv[0],
            },
            "time": int(time.time()),
        }

        if record.traceback:
            message_object["metadata"]["traceback"] = record.traceback

        return json.dumps(message_object)


class CustomLogger(logging.Logger):
    """
    Custom logger implementation
    """

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=None):
        if extra is None:
            extra = {}
        if "traceback" not in extra:
            extra["traceback"] = ""

        super(CustomLogger, self)._log(level, msg, args, exc_info, extra, stack_info)


logging.setLoggerClass(CustomLogger)
lifeguard_logger = logging.getLogger("lifeguard")
lifeguard_logger.propagate = 0
lifeguard_logger.setLevel(getattr(logging, LOG_LEVEL))

LIFEGUARD_HANDLER = logging.StreamHandler()
LIFEGUARD_HANDLER.setFormatter(CustomFormatter())

lifeguard_logger.addHandler(LIFEGUARD_HANDLER)
