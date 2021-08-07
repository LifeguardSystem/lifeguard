"""
Common assets controllers
"""
import io
from os.path import join

from lifeguard.controllers import Response, register_custom_controller, send_status
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import LIFEGUARD_DIRECTORY


def send_file(path, content_type):
    with open(join(LIFEGUARD_DIRECTORY, "public", path), "rb") as file:
        response = Response()
        response.content = io.BytesIO(file.read())
        response.content_type = content_type
        return response


def send_css(path):
    try:
        logger.info("returning css %s", path)
        return send_file("css/{}".format(path), "text/css")
    except:
        return send_status(404)


def send_js(path):
    try:
        logger.info("returning js %s", path)
        return send_file("js/{}".format(path), "application/javascript")
    except:
        return send_status(404)


def send_img(path):
    try:
        logger.info("returning img %s", path)
        return send_file("img/{}".format(path), "image/jpeg")
    except:
        return send_status(404)


def load_assets_controllers():
    register_custom_controller("/img/<path:path>", send_img, {"methods": ["GET"]})
    register_custom_controller("/js/<path:path>", send_js, {"methods": ["GET"]})
    register_custom_controller("/css/<path:path>", send_css, {"methods": ["GET"]})
