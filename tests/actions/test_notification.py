import unittest
from unittest.mock import MagicMock, patch

from lifeguard import NORMAL
from lifeguard.notifications import NotificationBase, NotificationStatus
from lifeguard.actions.notifications import (
    NOTIFICATION_METHODS,
    notify_in_single_message,
    notify_in_thread,
)


class TestActionNotification(unittest.TestCase):
    def setUp(self):
        NOTIFICATION_METHODS.clear()

        self.mock_implementation = MagicMock(name="mock_implementation")

        class MockNotificationBase(NotificationBase):
            def send_single_message(self, content, settings):
                super().send_single_message(content, settings)
                self.mock_implementation.send_single_message(content, settings)

        self.mock_notification_instance = MockNotificationBase()
        self.mock_notification_instance.mock_implementation = self.mock_implementation

        self.mock_validation_response = MagicMock(name="mock_validation_response")
        self.mock_validation_response.settings = None
        self.mock_settings = {}

    @patch(
        "lifeguard.actions.notifications.NOTIFICATION_IMPLEMENTATIONS",
        "mock.Implementation",
    )
    @patch("lifeguard.actions.notifications.load_implementation")
    def test_should_not_send_notify_in_single_message(self, mock_load_implementation):
        mock_load_implementation.return_value = self.mock_notification_instance

        notify_in_single_message(self.mock_validation_response, self.mock_settings)

        mock_load_implementation.assert_called_with("mock.Implementation")

    @patch(
        "lifeguard.actions.notifications.NOTIFICATION_IMPLEMENTATIONS",
        "mock.Implementation",
    )
    @patch("lifeguard.actions.notifications.load_implementation")
    def test_should_send_notify_in_single_message(self, mock_load_implementation):
        mock_load_implementation.return_value = self.mock_notification_instance

        self.mock_validation_response.settings = {"notification": {"notify": True}}
        self.mock_validation_response.details = {"status": "PROBLEM"}

        notify_in_single_message(self.mock_validation_response, self.mock_settings)

        self.mock_implementation.send_single_message.assert_called_with(
            '{"status": "PROBLEM"}', {}
        )

    @patch("lifeguard.actions.notifications.load_implementation")
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    def test_should_send_notify_in_thread_not_problem_and_not_last_notification(
        self, mock_notification_repository, mock_json, mock_load_implementation
    ):
        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = (
            None
        )

        mock_load_implementation.return_value = self.mock_notification_instance

        self.mock_validation_response.status = NORMAL

        notify_in_thread(self.mock_validation_response, self.mock_settings)

        mock_json.dumps.assert_not_called()

    @patch(
        "lifeguard.actions.notifications.NOTIFICATION_IMPLEMENTATIONS",
        "mock.Implementation",
    )
    @patch("lifeguard.actions.notifications.load_implementation")
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    def test_should_send_notify_in_thread_not_problem_and_last_notification(
        self, mock_notification_repository, mock_json, mock_load_implementation
    ):
        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = NotificationStatus(
            "validation", {"not implemented": "thread"}
        )

        mock_load_implementation.return_value = self.mock_notification_instance

        self.mock_validation_response.status = NORMAL
        self.mock_validation_response.details = {}

        notify_in_thread(self.mock_validation_response, self.mock_settings)
