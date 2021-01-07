import unittest
from unittest.mock import MagicMock, patch

from lifeguard.notifications import (
    NOTIFICATION_METHODS,
    append_notification_implementation,
)


mock_logger = MagicMock(name="mock_logger")


class TestNotifications(unittest.TestCase):
    def setUp(self):
        NOTIFICATION_METHODS.clear()

    @patch("lifeguard.notifications.logger", mock_logger)
    def test_append_notification_implementation(self):
        implementation = MagicMock(name="implementation")
        implementation.__name__ = "implementation"
        implementation_instance = MagicMock(name="instance")
        implementation.return_value = implementation_instance

        append_notification_implementation(implementation)
        self.assertTrue(implementation_instance in NOTIFICATION_METHODS)
        mock_logger.info.assert_called_with(
            "appending implementation %s", implementation.__name__
        )

    @patch("lifeguard.notifications.logger", mock_logger)
    def test_append_notification_implementation_and_not_duplicate(self):
        class NotificationImplementation:
            pass

        append_notification_implementation(NotificationImplementation)
        append_notification_implementation(NotificationImplementation)

        self.assertEqual(1, len(NOTIFICATION_METHODS))
