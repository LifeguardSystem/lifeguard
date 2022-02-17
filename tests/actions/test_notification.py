import unittest
from unittest.mock import MagicMock, patch

from lifeguard import NORMAL, PROBLEM
from lifeguard.notifications import (
    NotificationBase,
    NotificationStatus,
)
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

    @patch("lifeguard.actions.notifications.HistoryRepository")
    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_in_single_message(self, mock_history_repository):
        history_repository_instance = MagicMock(name="history_repository")
        mock_history_repository.return_value = history_repository_instance

        self.mock_validation_response.validation_name = "validation_name"
        self.mock_validation_response.settings = {"notification": {"notify": True}}
        self.mock_validation_response.details = {"status": "PROBLEM"}
        self.mock_validation_response.status = PROBLEM

        notify_in_single_message(
            self.mock_validation_response, {"notification": {"add_to_history": True}}
        )

        mock_implementation.send_single_message.assert_called_with(
            '{"status": "PROBLEM"}', {"notification": {"add_to_history": True}}
        )
        notification_occurrence = (
            history_repository_instance.append_notification.call_args[0][0]
        )

        self.assertEqual(notification_occurrence.notification_type, "single")
        self.assertEqual(notification_occurrence.validation_name, "validation_name")
        self.assertEqual(notification_occurrence.details, {"status": "PROBLEM"})
        self.assertEqual(notification_occurrence.status, "PROBLEM")

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_in_single_message_with_template(self):
        self.mock_validation_response.settings = {
            "notification": {
                "notify": True,
                "data": {"user": "a user", "body": "message body"},
            }
        }
        self.mock_validation_response.details = {"status": "PROBLEM"}

        self.mock_settings["notification"] = {
            "template": """Hello {{user}},
{{body}}
"""
        }

        notify_in_single_message(self.mock_validation_response, self.mock_settings)

        mock_implementation.send_single_message.assert_called_with(
            "Hello a user,\nmessage body",
            {"notification": {"template": "Hello {{user}},\n{{body}}\n"}},
        )

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_multiple_notify_in_single_message_with_template(self):
        self.mock_validation_response.settings = {
            "notification": {
                "notify": True,
                "data": [
                    {"user": "first user", "body": "message body"},
                    {"user": "second user", "body": "message body"},
                ],
            }
        }
        self.mock_validation_response.details = {"status": "PROBLEM"}

        self.mock_settings["notification"] = {
            "template": """Hello {{user}},
{{body}}
"""
        }

        notify_in_single_message(self.mock_validation_response, self.mock_settings)

        mock_implementation.send_single_message.assert_called_with(
            ["Hello first user,\nmessage body", "Hello second user,\nmessage body"],
            {"notification": {"template": "Hello {{user}},\n{{body}}\n"}},
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
    @patch("lifeguard.actions.notifications.HistoryRepository")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_open_thread(
        self, mock_notification_repository, mock_history_repository, mock_json
    ):
        history_repository_instance = MagicMock(name="history_repository")
        mock_history_repository.return_value = history_repository_instance

        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = (
            None
        )

        mock_json.dumps.return_value = "{}"

        self.mock_validation_response.validation_name = "validation_name"
        self.mock_validation_response.status = PROBLEM
        self.mock_validation_response.details = {}

        notify_in_thread(
            self.mock_validation_response, {"notification": {"add_to_history": True}}
        )

        mock_implementation.init_thread.assert_called_with(
            "{}", {"notification": {"add_to_history": True}}
        )

        notification_occurrence = (
            history_repository_instance.append_notification.call_args[0][0]
        )

        self.assertEqual(notification_occurrence.notification_type, "init_thread")
        self.assertEqual(notification_occurrence.validation_name, "validation_name")
        self.assertEqual(notification_occurrence.details, {})
        self.assertEqual(notification_occurrence.status, "PROBLEM")

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.HistoryRepository")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_close_thread(
        self, mock_notification_repository, mock_history_repository, mock_json
    ):

        history_repository_instance = MagicMock(name="history_repository")
        mock_history_repository.return_value = history_repository_instance

        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = NotificationStatus(
            "validation", {"not implemented": "thread"}
        )

        mock_json.dumps.return_value = "{}"

        self.mock_validation_response.status = NORMAL
        self.mock_validation_response.details = {}

        notify_in_thread(
            self.mock_validation_response, {"notification": {"add_to_history": True}}
        )

        mock_implementation.close_thread.assert_called_with(
            "thread", "{}", {"notification": {"add_to_history": True}}
        )

        notification_occurrence = (
            history_repository_instance.append_notification.call_args[0][0]
        )

        self.assertEqual(notification_occurrence.notification_type, "close_thread")

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.HistoryRepository")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_send_notify_update_thread(
        self, mock_notification_repository, mock_history_repository, mock_json
    ):
        history_repository_instance = MagicMock(name="history_repository")
        mock_history_repository.return_value = history_repository_instance

        notification_repository_instance = MagicMock(name="repository")
        mock_notification_repository.return_value = notification_repository_instance
        notification_repository_instance.fetch_last_notification_for_a_validation.return_value = NotificationStatus(
            "validation", {"not implemented": "thread"}
        )

        mock_json.dumps.return_value = "{}"

        self.mock_validation_response.status = PROBLEM
        self.mock_validation_response.details = {}

        notify_in_thread(
            self.mock_validation_response, {"notification": {"add_to_history": True}}
        )

        mock_implementation.update_thread.assert_called_with(
            "thread", "{}", {"notification": {"add_to_history": True}}
        )

        notification_occurrence = (
            history_repository_instance.append_notification.call_args[0][0]
        )

        self.assertEqual(notification_occurrence.notification_type, "update_thread")

    @patch("lifeguard.actions.notifications.NOTIFICATION_METHODS", NOTIFICATION_METHODS)
    @patch("lifeguard.actions.notifications.json")
    @patch("lifeguard.actions.notifications.NotificationRepository")
    @patch("lifeguard.actions.notifications.logger", mock_logger)
    def test_should_not_update_thread_if_into_interval(
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

        notify_in_thread(
            self.mock_validation_response,
            {"notification": {"update_thread_interval": 60}},
        )

        mock_implementation.update_thread.assert_not_called()
