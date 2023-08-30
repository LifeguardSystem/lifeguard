import traceback

from lifeguard.controllers import register_custom_controller, send_status
from lifeguard.groups import build_groups_summary, build_group_validations_list
from lifeguard.logger import lifeguard_logger as logger


def groups_summary_controller():
    try:
        return build_groups_summary()
    except Exception as error:
        logger.error(
            "error on build groups summary: %s",
            error,
            extra={"traceback": traceback.format_exc()},
        )
        return send_status(
            500,
            content_type="application/json",
        )


def groups_controller(group):
    try:
        return build_group_validations_list(group)
    except Exception as error:
        logger.error(
            "error on build group validations list: %s",
            error,
            extra={"traceback": traceback.format_exc()},
        )
        return send_status(
            500,
            content_type="application/json",
        )


def load_groups_controllers():
    register_custom_controller(
        "/lifeguard/groups/summary", groups_summary_controller, {"methods": ["GET"]}
    )
    register_custom_controller(
        "/lifeguard/groups/<group>", groups_controller, {"methods": ["GET"]}
    )
