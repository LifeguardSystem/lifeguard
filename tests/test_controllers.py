import unittest
from unittest.mock import MagicMock, patch, ANY

from lifeguard.controllers import load_custom_controllers

from tests.fixtures.controllers.hello_controller import hello


class TestControllers(unittest.TestCase):
    @patch("lifeguard.controllers.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.controllers.logger")
    @patch("lifeguard.controllers.custom_controllers")
    def test_load_custom_controllers(self, mock_custom_controllers, mock_logger):
        load_custom_controllers()
        mock_logger.info.assert_any_call(
            "loading custom controller %s", "hello_controller"
        )
        mock_custom_controllers.add_url_rule.assert_called_with("/hello", "hello", ANY)
        self.assertEqual("hello", hello())
