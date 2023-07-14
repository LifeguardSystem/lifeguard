import unittest
from unittest.mock import patch, MagicMock, call

from lifeguard.scheduler import (
    configure_validations,
    VALID_TIME_PERIODS,
    MOMENTS,
    check_if_should_reload,
    reload_scheduler,
    start_scheduler,
    WATCHED_FILES,
)

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

    @patch("lifeguard.scheduler.clear_validations")
    @patch("lifeguard.scheduler.load_validations")
    @patch("lifeguard.scheduler.configure_validations")
    @patch("lifeguard.scheduler.schedule")
    def test_reload_scheduler(
        self,
        mock_schedule,
        mock_configure_validations,
        mock_load_validations,
        mock_clear_validations,
    ):
        reload_scheduler()

        mock_schedule.clear.assert_called_with("validation")
        mock_configure_validations.assert_called_with()
        mock_load_validations.assert_called_with()
        mock_clear_validations.assert_called_with()

    @patch("lifeguard.scheduler.FOREVER", False)
    @patch("lifeguard.scheduler.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.scheduler.configure_validations")
    @patch("lifeguard.scheduler.getmtime")
    def test_start_scheduler(self, mock_getmtime, mock_configure_validations):
        mock_getmtime.return_value = 1

        start_scheduler()

        mock_configure_validations.assert_called_with()
        self.assertEqual(
            WATCHED_FILES, {"tests/fixtures/validations/simple_validation.yaml": 1}
        )

    @patch("lifeguard.scheduler.WATCHED_FILES", {})
    @patch("lifeguard.scheduler.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.scheduler.reload_scheduler")
    @patch("lifeguard.scheduler.logger")
    def test_check_if_should_reload_with_new_file(
        self, mock_logger, mock_reload_scheduler
    ):
        check_if_should_reload()
        mock_reload_scheduler.assert_called_with()
        mock_logger.info.assert_has_calls(
            [
                call(
                    "watching file %s",
                    "tests/fixtures/validations/simple_validation.yaml",
                )
            ]
        )

    @patch(
        "lifeguard.scheduler.WATCHED_FILES",
        {"tests/fixtures/validations/simple_validation.yaml": 1},
    )
    @patch("lifeguard.scheduler.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.scheduler.reload_scheduler")
    @patch("lifeguard.scheduler.logger")
    def test_check_if_should_reload_with_file_changed(
        self, mock_logger, mock_reload_scheduler
    ):
        check_if_should_reload()
        mock_reload_scheduler.assert_called_with()
        mock_logger.info.assert_has_calls(
            [
                call(
                    "file changed %s",
                    "tests/fixtures/validations/simple_validation.yaml",
                )
            ]
        )

    @patch(
        "lifeguard.scheduler.WATCHED_FILES",
        {"tests/fixtures/validations/not_exists.yaml": 1},
    )
    @patch("lifeguard.scheduler.LIFEGUARD_DIRECTORY", "tests/fixtures")
    @patch("lifeguard.scheduler.reload_scheduler")
    @patch("lifeguard.scheduler.logger")
    def test_check_if_should_reload_with_file_removed(
        self, mock_logger, mock_reload_scheduler
    ):
        check_if_should_reload()
        mock_reload_scheduler.assert_called_with()
        mock_logger.info.assert_has_calls(
            [call("file removed %s", "tests/fixtures/validations/not_exists.yaml")]
        )
