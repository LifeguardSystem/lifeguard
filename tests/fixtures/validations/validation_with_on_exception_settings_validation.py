from lifeguard import PROBLEM
from lifeguard.validations import ValidationResponse, validation


def simple_action(_response, _settings):
    pass


@validation(
    description="simple description",
    actions=[simple_action],
    settings={
        "on_exception": {
            "result": ValidationResponse(
                "validation_with_on_exception_settings", PROBLEM, {}
            ),
            "append_traceback_on_details": True,
            "rerun_actions": True,
        }
    },
)
def validation_with_on_exception_settings():
    raise Exception("error")
