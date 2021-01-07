import unittest
from unittest.mock import MagicMock, patch

from lifeguard import NORMAL, PROBLEM
from lifeguard.notifications import NotificationBase, NotificationStatus
from lifeguard.actions.notifications import (
    notify_in_single_message,
    notify_in_thread,
)

mock_implementation = MagicMock(name="mock_implementation")
mock_logger = MagicMock(name="logger")


class MockNotificationBase(NotificationBase):
    def __init__(self):
        self.mock_implementation = None

    def send_single_message(self, content, settings):
        super().send_single_message(content, settings)
        self.mock_implementation.send_single_message(content, settings)

    def init_thread(self, content, settings):
        super().init_thread(content, settings)
        self.mock_implementation.init_thread(content, settings)

    def update_thread(self, thread_id, content, settings):
        super().update_thread(thread_id, content, settings)
        self.mock_implementation.update_thread(thread_id, content, settings)

    def close_thread(self, thread_id, content, settings):
        super().close_thread(thread_id, content, settings)
        self.mock_implementation.close_thread(thread_id, content, settings)


mock_notification_instance = MockNotificationBase()
mock_notification_instance.mock_implementation = mock_implementation


NOTIFICATION_METHODS = [mock_notification_instance]


class TestActionNotification(unittest.TestCase):
    def setUp(self):

        self.mock_validation_response = MagicMock(name="mock_validation_response")
        self.mock_validation_response.settings = None
        self.mock_settings = {}

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", [])
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_not_send_notify_in_single_message(self):

        notify_in_single_message(self.mock_validation_response, self.mock_settings)
        mock_implementation.send_single_message.assert_not_called()

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_in_single_message(self):
        self.mock_validation_response.settings = {"notification": {"notify": True}}
        self.mock_validation_response.details = {"status": "PROBLEM"}

        notify_in_single_message(self.mock_validation_response, self.mock_settings)

        mock_implementation.send_single_message.assert_called_with(
            '{"status": "PROBLEM"}', {}
        )

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_in_thread_not_problem_and_not_last_notification(
        self, mock_notification_repository, mock_json
    ):
        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = (
            None
        )

        self.mock_validation_response.status = NORMAL

        notify_in_thread(self.mock_validation_response, self.mock_settings)

        mock_json.dumps.assert_not_called()

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_open_thread(
        self, mock_notification_repository, mock_json
    ):
        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = (
            None
        )

        mock_json.dumps.return_value = "{}"

        self.mock_validation_response.status = PROBLEM
        self.mock_validation_response.details = {}

        notify_in_thread(self.mock_validation_response, self.mock_settings)

        mock_implementation.init_thread.assert_called_with("{}", {})

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_close_thread(
        self, mock_notification_repository, mock_json
    ):
        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = NotificationStatus(
            "validation", {"not implemented": "thread"}
        )

        mock_json.dumps.return_value = "{}"

        self.mock_validation_response.status = NORMAL
        self.mock_validation_response.details = {}

        notify_in_thread(self.mock_validation_response, self.mock_settings)

        mock_implementation.close_thread.assert_called_with("thread", "{}", {})

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_update_thread(
        self, mock_notification_repository, mock_json
    ):
        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = NotificationStatus(
            "validation", {"not implemented": "thread"}
        )

        mock_json.dumps.return_value = "{}"

        self.mock_validation_response.status = PROBLEM
        self.mock_validation_response.details = {}

        notify_in_thread(self.mock_validation_response, self.mock_settings)

        mock_implementation.update_thread.assert_called_with("thread", "{}", {})
