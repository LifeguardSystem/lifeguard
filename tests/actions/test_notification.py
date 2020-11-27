import unittest
from unittest.mock import MagicMock, patch

from lifeguard.notifications import NotificationBase
from lifeguard.actions.notifications import (
    NOTIFICATION_METHODS,
    notify_in_single_message,
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
