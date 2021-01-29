import unittest
from unittest.mock import MagicMock, mock_open, patch

from lifeguard.bootstrap import generate_base_project


class TestBootstrap(unittest.TestCase):
    @patch("lifeguard.bootstrap.os")
    def test_generate_base_project(self, mock_os):

        mock_os.path.exists.return_value = False

        mocked_open = mock_open()

        with patch("builtins.open", mocked_open, create=True):
            generate_base_project()

        mocked_open.assert_called_with("lifeguard_settings.py", "w")

        mocked_file = mocked_open()
        mocked_file.write.assert_called_with(
            "\nPLUGINS = []\n\ndef setup(_lifeguard_context):\n    pass\n"
        )

        mock_os.path.exists.assert_called_with("validations")
        mock_os.makedirs.assert_called_with("validations")
