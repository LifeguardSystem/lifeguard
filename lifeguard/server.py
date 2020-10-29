import json
import pathlib
import traceback
from datetime import datetime
from os.path import join

from flask import Flask, Response, render_template, request, make_response

from lifeguard import NORMAL, change_status
from lifeguard.dashboard.download import classifications, error_rate
from lifeguard.dashboard.nfs import nfs_space_left
from lifeguard.dashboard.occurrences import latests_occurrences
from lifeguard.infrastructure.mongodb import (
    find_occurrences,
    read_results,
    read_results_not_normal,
    recover_modules,
    save_module,
    save_node_status,
    read_settings,
)
from lifeguard.quality import evaluate_metric, evaluate_last_analysis
from lifeguard.json import converter
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.validations.agents import validate_agent
from lifeguard.validations.alertmanager import validate_alertmanager

STATIC_FOLDER = "public"
APP = Flask(__name__, static_folder=STATIC_FOLDER)


def send_file(path):
    absolute_path = pathlib.Path(__file__).parent.absolute()
    with open(join(absolute_path, STATIC_FOLDER, path), "r") as file:
        return file.read()


def __to_datetime(value):
    if value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")


@APP.route("/lifeguard/status")
def global_status():
    try:
        details = []
        status = NORMAL
        for result in read_results_not_normal():
            details.append(result)
            status = change_status(status, result["status"])
        return json.dumps({"status": status, "details": details}, default=converter)
    except Exception:
        logger.error(
            "error on recover global status",
            extra={"traceback": traceback.format_exc()},
        )
        return json.dumps({"error": traceback.format_exc()})


@APP.route("/lifeguard/status/<health>")
def return_status(health):
    try:
        result = read_results(health)
        result.pop("_id")

        response = make_response(json.dumps(result, default=converter))
        response.headers["Content-Type"] = "application/json"

        return response
    except Exception:
        logger.error(
            "error on recover status for %s",
            health,
            extra={"traceback": traceback.format_exc()},
        )
        return json.dumps({"error": traceback.format_exc()})
