from lifeguard import NORMAL
from lifeguard.validations import ValidationResponse, validation


@validation(description="simple description", actions=[], settings={})
def simple_subdir_validation():
    return ValidationResponse("simple_subdir_validation", NORMAL, {})
