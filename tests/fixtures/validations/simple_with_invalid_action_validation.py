from lifeguard import NORMAL
from lifeguard.validations import ValidationResponse, validation


def invalid_action():
    pass


@validation(description="simple description", actions=[invalid_action])
def simple_with_invalid_action_validation():
    return ValidationResponse("simple_with_invalid_action_validation", NORMAL, {})
