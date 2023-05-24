NORMAL = "NORMAL"
WARNING = "WARNING"
PROBLEM = "PROBLEM"

ACTION_STATUSES = [NORMAL, WARNING, PROBLEM]


def change_status(old, new):
    """
    Change status by severity
    """
    if ACTION_STATUSES.index(new) > ACTION_STATUSES.index(old):
        return new
    return old
