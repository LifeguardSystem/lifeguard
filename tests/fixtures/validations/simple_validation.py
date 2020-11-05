from lifeguard import NORMAL
from lifeguard.validations import ValidationResponse, validation


@validation(description="simple description", actions=[])
def simple_validation():
    return ValidationResponse("simple_validation", NORMAL, {})
