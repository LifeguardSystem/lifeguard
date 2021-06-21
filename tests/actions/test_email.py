import unittest
from unittest.mock import patch, MagicMock

from lifeguard import NORMAL, PROBLEM
from lifeguard.actions.email import send_email, EMAIL_NOTIFICATIONS


class ActionEmailTest(unittest.TestCase):
    @patch("lifeguard.actions.email.logger")
    @patch("lifeguard.actions.email.smtplib")
    def test_send_email(self, mock_smtplib, mock_logger):
        mock_session = MagicMock(name="session")
        mock_smtplib.SMTP.return_value = mock_session

        validation_response = MagicMock(name="validation_response")
        validation_response.validation_name = "validation_with_problem"
        validation_response.status = PROBLEM
        validation_response.details = {"status": PROBLEM}
        send_email(
            validation_response,
            {
                "email": {
                    "subject": "subject example",
                    "receivers": [{"name": "name", "email": "email@server.com"}],
                    "send_in": [PROBLEM],
                }
            },
        )

        mock_smtplib.SMTP.assert_called_with("smtp_server", port="smtp_port")
        mock_session.starttls.assert_called()
        mock_session.login.assert_called_with("smtp_user", "smtp_passwd")
        mock_session.sendmail.assert_called_with(
            "smtp_user",
            ["email@server.com"],
            "From: smtp_user\nTo: name <email@server.com>\nMIME-Version: 1.0\nContent-type: text/html\nSubject: subject example\n\n<h1>Validation details</h1>\n\n<quote>\n{'status': 'PROBLEM'}\n</quote>\n\n<hr/>\n<p>\n    See more details in Lifeguard Dashboard: http://localhost:5567.\n</p>\n",
        )
        mock_session.quit.assert_called()
        mock_logger.info.assert_called_with(
            "sending email %s to %s",
            "From: smtp_user\nTo: name <email@server.com>\nMIME-Version: 1.0\nContent-type: text/html\nSubject: subject example\n\n<h1>Validation details</h1>\n\n<quote>\n{'status': 'PROBLEM'}\n</quote>\n\n<hr/>\n<p>\n    See more details in Lifeguard Dashboard: http://localhost:5567.\n</p>\n",
            ["email@server.com"],
        )
        self.assertTrue(validation_response.validation_name in EMAIL_NOTIFICATIONS)

    @patch("lifeguard.actions.email.logger")
    @patch("lifeguard.actions.email.smtplib")
    def test_not_send_email(self, mock_smtplib, mock_logger):
        mock_session = MagicMock(name="session")
        mock_smtplib.SMTP.return_value = mock_session

        validation_response = MagicMock(name="validation_response")
        validation_response.validation_name = "validation_test"
        validation_response.status = NORMAL
        validation_response.details = {}

        send_email(
            validation_response,
            {
                "email": {
                    "subject": "subject example",
                    "receivers": [{"name": "name", "email": "email@server.com"}],
                }
            },
        )

        mock_logger.info.assert_not_called()

    @patch("lifeguard.actions.email.logger")
    @patch("lifeguard.actions.email.smtplib")
    def test_remove_validation_from_sent_list(self, mock_smtplib, mock_logger):
        mock_session = MagicMock(name="session")
        mock_smtplib.SMTP.return_value = mock_session

        validation_response = MagicMock(name="validation_response")
        validation_response.validation_name = "validation_in_list"
        validation_response.status = NORMAL
        validation_response.details = {}

        EMAIL_NOTIFICATIONS["validation_in_list"] = {}

        send_email(
            validation_response,
            {
                "email": {
                    "subject": "subject example",
                    "receivers": [{"name": "name", "email": "email@server.com"}],
                }
            },
        )

        mock_logger.info.assert_not_called()
        self.assertTrue("validation_in_list" not in EMAIL_NOTIFICATIONS)

    @patch("lifeguard.actions.email.traceback")
    @patch("lifeguard.actions.email.logger")
    @patch("lifeguard.actions.email.smtplib")
    def test_error_on_send_email(self, mock_smtplib, mock_logger, mock_traceback):
        mock_session = MagicMock(name="session")
        mock_smtplib.SMTP.return_value = mock_session

        mock_session.starttls.side_effect = Exception("tls error")

        validation_response = MagicMock(name="validation_response")
        validation_response.status = PROBLEM
        validation_response.details = {}

        mock_traceback.format_exc.return_value = "format_exc"

        send_email(
            validation_response,
            {
                "email": {
                    "subject": "subject example",
                    "receivers": [{"name": "name", "email": "email@server.com"}],
                    "send_in": [PROBLEM],
                }
            },
        )

        mock_logger.error.assert_called_with(
            "error on send email %s to %s",
            "From: smtp_user\nTo: name <email@server.com>\nMIME-Version: 1.0\nContent-type: text/html\nSubject: subject example\n\n<h1>Validation details</h1>\n\n<quote>\n{}\n</quote>\n\n<hr/>\n<p>\n    See more details in Lifeguard Dashboard: http://localhost:5567.\n</p>\n",
            ["email@server.com"],
            extra={"traceback": "format_exc"},
        )
