import unittest

from lifeguard import (
    change_status,
    NORMAL,
    WARNING,
    PROBLEM,
    VERSION,
    ACTION_STATUSES,
)


class TestLifeguardCore(unittest.TestCase):
    def test_current_version(self):
        self.assertEqual(VERSION, "0.0.1")

    def test_statuses(self):
        self.assertEqual(NORMAL, "NORMAL")
        self.assertEqual(WARNING, "WARNING")
        self.assertEqual(PROBLEM, "PROBLEM")
        self.assertEqual(ACTION_STATUSES, [NORMAL, WARNING, PROBLEM])

    def test_change_status(self):
        self.assertEqual(change_status(NORMAL, NORMAL), NORMAL)
        self.assertEqual(change_status(NORMAL, WARNING), WARNING)
        self.assertEqual(change_status(PROBLEM, WARNING), PROBLEM)
