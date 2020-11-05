from lifeguard import ValidationResponse, validation, NORMAL


@validation(description="simple description", actions=[])
def simple_validation():
    return ValidationResponse("simple_validation", NORMAL, {})
