import unittest
from unittest.mock import patch, MagicMock

from lifeguard.scheduler import configure_validations, VALID_TIME_PERIODS, MOMENTS

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

    @patch(
        "lifeguard.scheduler.VALIDATIONS",
        {"example": {"ref": mock_ref, "schedule": {"every": {"hours": 1}}}},
    )
    @patch("lifeguard.scheduler.schedule")
    def test_configure_validations_every_hour(self, mock_schedule):
        configure_validations()

        mock_schedule.every.assert_called_with(1)

    @patch(
        "lifeguard.scheduler.VALIDATIONS",
        {"example": {"ref": mock_ref, "schedule": {"every": {"blah": 1}}}},
    )
    @patch("lifeguard.scheduler.schedule")
    def test_configure_validations_with_invalid_time_period(self, mock_schedule):
        configure_validations()

        mock_schedule.every.assert_not_called()

    @patch(
        "lifeguard.scheduler.VALIDATIONS",
        {"example": {"ref": mock_ref, "schedule": {"at": {"hour": "10:00"}}}},
    )
    @patch("lifeguard.scheduler.schedule")
    def test_configure_validations_at_specific_minute(self, mock_schedule):
        mock_do = MagicMock(name="do")

        mock_at = MagicMock(name="at")
        mock_at.at.return_value = mock_do

        mock_return_of_every = MagicMock(name="mock_return_of_every")
        mock_schedule.every.return_value = mock_return_of_every
        mock_return_of_every.hour = mock_at

        configure_validations()

        mock_schedule.every.assert_called()
        mock_at.at.assert_called_with("10:00")
        mock_do.do.assert_called_with(mock_ref)

    def test_valid_time_periods(self):
        self.assertEqual(
            VALID_TIME_PERIODS,
            [
                "seconds",
                "minutes",
                "hours",
                "days",
                "weeks",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
        )

    def test_moments(self):
        self.assertEqual(
            MOMENTS,
            [
                "second",
                "minute",
                "hour",
                "day",
                "week",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
        )
