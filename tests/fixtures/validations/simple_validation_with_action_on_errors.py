from lifeguard.validations import validation

from unittest.mock import MagicMock

ON_ERROR_ACTION_MOCK = MagicMock(name="on_error_action")


def on_error_action(result, settings):
    ON_ERROR_ACTION_MOCK(result, settings)


@validation(
    description="execute error action",
    actions=[],
    actions_on_error=[on_error_action],
    settings={},
)
def simple_validation_with_action_on_errors():
    raise RuntimeError("error")
