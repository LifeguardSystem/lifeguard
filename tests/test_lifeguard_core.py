import unittest
from unittest.mock import patch

from lifeguard import (
    change_status,
    setup,
    NORMAL,
    WARNING,
    PROBLEM,
    VERSION,
    ACTION_STATUSES,
)


class TestLifeguardCore(unittest.TestCase):
    def test_current_version(self):
        self.assertEqual(VERSION, "0.0.4")

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
    def test_setup_call_load_validations(self, mock_load_validations):
        setup()
        mock_load_validations.assert_called()

    @patch("lifeguard.declare_implementation")
    @patch("lifeguard.load_validations")
    def test_setup_call_init_validation_persistence_layer(
        self, _mock_load_validations, mock_declare_implementation
    ):
        setup()
        mock_declare_implementation.assert_called_with("validation", None)
