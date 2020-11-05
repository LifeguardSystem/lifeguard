from lifeguard import NORMAL
from lifeguard.validations import ValidationResponse, validation


def simple_action(_response):
    pass


@validation(description="simple description", actions=[simple_action])
def simple_with_action_validation():
    return ValidationResponse("simple_with_action_validation", NORMAL, {})
