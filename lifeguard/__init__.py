"""
Lifeguard validation core
"""

VERSION = VERSION = "0.0.2"

NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]


def change_status(old, new):
    if ACTION_STATUSES.index(new) > ACTION_STATUSES.index(old):
        return new
    return old
