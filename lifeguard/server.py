import json
import traceback
from datetime import datetime

from flask import Flask, make_response

from lifeguard import NORMAL, PROBLEM, change_status
from lifeguard.controllers import custom_controllers, login_required
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.repositories import ValidationRepository
from lifeguard.validations import VALIDATIONS, ValidationResponseEncoder

APP = Flask(__name__)


def make_json_response(content):
    """
    Make default json response
    """
    response = make_response(content)
    response.headers["Content-Type"] = "application/json"
    return response


def build_global_status(complete=False):
    """
    Build global status method
    """
    try:
        response = {"status": NORMAL, "validations": []}
        repository = ValidationRepository()
        for validation in repository.fetch_all_validation_results():
            response["status"] = change_status(response["status"], validation.status)
            if complete or validation.status != NORMAL:
                response["validations"].append(validation)
        return make_json_response(ValidationResponseEncoder().encode(response))
    except Exception:
        logger.error(
            "error on execute get status",
            extra={"traceback": traceback.format_exc()},
        )
        return make_json_response(json.dumps({"error": traceback.format_exc()}))


@APP.route("/lifeguard/status", methods=["GET"])
@login_required
def get_status():
    """
    Return global status
    """
    return build_global_status()


@APP.route("/lifeguard/status/complete", methods=["GET"])
@login_required
def get_status_complete():
    """
    Return global status with details
    """
    return build_global_status(True)


@APP.route("/lifeguard/validations/<validation>", methods=["GET"])
@login_required
def get_validation(validation):
    repository = ValidationRepository()
    result = repository.fetch_last_validation_result(validation)
    return make_json_response(ValidationResponseEncoder().encode(result))


@APP.route("/lifeguard/validations/<validation>/execute", methods=["POST"])
@login_required
def execute_validation(validation):
    try:
        result = VALIDATIONS[validation]["ref"]()
        result.last_execution = datetime.now()
        return make_json_response(ValidationResponseEncoder().encode(result))
    except Exception:
        logger.error(
            "error on execute validation %s",
            validation,
            extra={"traceback": traceback.format_exc()},
        )
        return json.dumps({"error": traceback.format_exc()})


APP.register_blueprint(custom_controllers)
