import unittest
from unittest.mock import MagicMock, mock_open, patch, call

from lifeguard.controllers.assets import (
    send_file,
    send_css,
    send_js,
    send_img,
    load_assets_controllers,
)


class TestAssetsControllers(unittest.TestCase):
    @patch("lifeguard.controllers.assets.join")
    @patch("lifeguard.controllers.assets.io")
    def test_send_file(self, mock_io, mock_join):
        with patch("builtins.open", new_callable=mock_open()) as mock:
            mock_join.return_value = ""

            mock_io.BytesIO.return_value = "io"

            mock_file = MagicMock(instance="file")
            mock_file.read.return_value = "".encode("utf-8")
            mock.return_value.__enter__.return_value = mock_file

            response = send_file("file", "image/jpeg")

            self.assertDictEqual(
                response.__dict__,
                {
                    "_content": "io",
                    "_content_type": "image/jpeg",
                    "_data": {},
                    "_status": 200,
                    "_template": None,
                    "_template_searchpath": None,
                },
            )

            mock.assert_called_with("", "rb")
            mock_join.assert_called_with(".", "public", "file")
            mock_io.BytesIO.assert_called_with(b"")

    @patch("lifeguard.controllers.assets.send_file")
    @patch("lifeguard.controllers.assets.logger")
    def test_send_css(self, mock_logger, mock_send_file):
        mock_send_file.return_value = ""

        response = send_css("file.css")

        self.assertEqual(response, "")
        mock_send_file.assert_called_with("css/file.css", "text/css")
        mock_logger.info.assert_called_with("returning css %s", "file.css")

    @patch("lifeguard.controllers.assets.send_file")
    def test_send_css_not_found(self, mock_send_file):
        mock_send_file.side_effect = Exception("exception")

        response = send_css("file.css")

        self.assertEqual(
            response.__dict__,
            {
                "_content": None,
                "_content_type": "text/html",
                "_data": {},
                "_status": 404,
                "_template": None,
                "_template_searchpath": None,
            },
        )

    @patch("lifeguard.controllers.assets.send_file")
    @patch("lifeguard.controllers.assets.logger")
    def test_send_js(self, mock_logger, mock_send_file):
        mock_send_file.return_value = ""

        response = send_js("file.js")

        self.assertEqual(response, "")
        mock_send_file.assert_called_with("js/file.js", "application/javascript")
        mock_logger.info.assert_called_with("returning js %s", "file.js")

    @patch("lifeguard.controllers.assets.send_file")
    def test_send_js_not_found(self, mock_send_file):
        mock_send_file.side_effect = Exception("exception")

        response = send_js("file.js")

        self.assertEqual(
            response.__dict__,
            {
                "_content": None,
                "_content_type": "text/html",
                "_data": {},
                "_status": 404,
                "_template": None,
                "_template_searchpath": None,
            },
        )

    @patch("lifeguard.controllers.assets.send_file")
    @patch("lifeguard.controllers.assets.logger")
    def test_send_img(self, mock_logger, mock_send_file):
        mock_send_file.return_value = ""

        response = send_img("file.jpg")

        self.assertEqual(response, "")
        mock_send_file.assert_called_with("img/file.jpg", "image/jpeg")
        mock_logger.info.assert_called_with("returning img %s", "file.jpg")

    @patch("lifeguard.controllers.assets.send_file")
    def test_send_img_not_found(self, mock_send_file):
        mock_send_file.side_effect = Exception("exception")

        response = send_img("file.jpg")

        self.assertEqual(
            response.__dict__,
            {
                "_content": None,
                "_content_type": "text/html",
                "_data": {},
                "_status": 404,
                "_template": None,
                "_template_searchpath": None,
            },
        )

    @patch("lifeguard.controllers.assets.register_custom_controller")
    def test_load_assets_controllers(self, mock_register_custom_controller):
        load_assets_controllers()
        mock_register_custom_controller.assert_has_calls(
            [
                call("/img/<path:path>", send_img, {"methods": ["GET"]}),
                call("/js/<path:path>", send_js, {"methods": ["GET"]}),
                call("/css/<path:path>", send_css, {"methods": ["GET"]}),
            ]
        )
