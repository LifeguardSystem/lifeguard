import unittest
from unittest.mock import patch


from lifeguard import (
    change_status,
    setup,
    NORMAL,
    WARNING,
    PROBLEM,
    ACTION_STATUSES,
)
from lifeguard.context import LIFEGUARD_CONTEXT

from tests.fixtures import mock_lifeguard_settings


class TestLifeguardCore(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(NORMAL, "NORMAL")
        self.assertEqual(WARNING, "WARNING")
        self.assertEqual(PROBLEM, "PROBLEM")
        self.assertEqual(ACTION_STATUSES, [NORMAL, WARNING, PROBLEM])

    def test_change_status(self):
        self.assertEqual(change_status(NORMAL, NORMAL), NORMAL)
        self.assertEqual(change_status(NORMAL, WARNING), WARNING)
        self.assertEqual(change_status(PROBLEM, WARNING), PROBLEM)

    @patch("lifeguard.load_validations")
    @patch("lifeguard.recover_settings")
    def test_setup_call_load_validations(
        self, mock_recover_settings, mock_load_validations
    ):
        mock_recover_settings.return_value = mock_lifeguard_settings

        setup(LIFEGUARD_CONTEXT)
        mock_load_validations.assert_called()
