import unittest
from unittest.mock import patch, MagicMock

from lifeguard.scheduler import configure_validations

mock_ref = MagicMock(name="ref")


class TestScheduler(unittest.TestCase):
    @patch(
        "lifeguard.scheduler.VALIDATIONS",
        {"example": {"ref": mock_ref, "schedule": {"every": {"minutes": 1}}}},
    )
    @patch("lifeguard.scheduler.schedule")
    def test_configure_validations_every_minute(self, mock_schedule):
        configure_validations()

        mock_schedule.every.assert_called_with(1)
