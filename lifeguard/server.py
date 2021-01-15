import json
import traceback
from datetime import datetime

from flask import Flask, make_response

from lifeguard.controllers import custom_controllers
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.repositories import ValidationRepository
from lifeguard.validations import VALIDATIONS, ValidationResponseEncoder

APP = Flask(__name__)


def make_json_response(content):
    response = make_response(content)
    response.headers["Content-Type"] = "application/json"
    return response


@APP.route("/lifeguard/validations/<validation>", methods=["GET"])
def get_validation(validation):
    repository = ValidationRepository()
    result = repository.fetch_last_validation_result(validation)
    return make_json_response(ValidationResponseEncoder().encode(result))


@APP.route("/lifeguard/validations/<validation>/execute", methods=["POST"])
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
