"""
Action to send problem
"""
import smtplib
import traceback
from datetime import datetime

from lifeguard import NORMAL, PROBLEM
from lifeguard.context import LIFEGUARD_CONTEXT
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import (
    LIFEGUARD_EMAIL_SMTP_PASSWD,
    LIFEGUARD_EMAIL_SMTP_PORT,
    LIFEGUARD_EMAIL_SMTP_SERVER,
    LIFEGUARD_EMAIL_SMTP_USER,
    LIFEGUARD_PUBLIC_ADDRESS,
)

EMAIL_NOTIFICATIONS = {}


class Message:
    """
    Email render template
    """

    def __init__(self, receivers, subject, message, template):
        self.receivers = receivers
        self.subject = subject
        self.message = message
        self.template = template

    def render(self):
        """
        Render email to send
        """
        receivers_line = ",".join(
            [
                "{} <{}>".format(receiver["name"], receiver["email"])
                for receiver in self.receivers
            ]
        )
        return (
            self.template.replace("[[SMTP_USER]]", LIFEGUARD_EMAIL_SMTP_USER)
            .replace("[[RECEIVERS]]", receivers_line)
            .replace("[[SUBJECT]]", self.subject)
            .replace("[[MESSAGE]]", self.message)
            .replace("[[LIFEGUARD_PUBLIC_ADDRESS]]", LIFEGUARD_PUBLIC_ADDRESS)
        )


def send_email(validation_response, settings):
    """
    Send email action
    """

    if validation_response.status in settings["email"].get(
        "remove_from_sent_list_when", [NORMAL]
    ) and (validation_response.validation_name in EMAIL_NOTIFICATIONS):
        EMAIL_NOTIFICATIONS.pop(validation_response.validation_name)

    if (
        validation_response.status in settings["email"].get("send_in", [PROBLEM])
        and validation_response.validation_name not in EMAIL_NOTIFICATIONS
    ):
        EMAIL_NOTIFICATIONS[validation_response.validation_name] = {
            "sent_at": datetime.now()
        }

        message = Message(
            settings["email"]["receivers"],
            settings["email"]["subject"],
            str(validation_response.details),
            LIFEGUARD_CONTEXT.alert_email_template,
        )

        emails = [receiver["email"] for receiver in settings["email"]["receivers"]]
        logger.info("sending email %s to %s", message.render(), emails)
        try:
            session = smtplib.SMTP(
                LIFEGUARD_EMAIL_SMTP_SERVER, port=LIFEGUARD_EMAIL_SMTP_PORT
            )
            session.starttls()
            session.login(LIFEGUARD_EMAIL_SMTP_USER, LIFEGUARD_EMAIL_SMTP_PASSWD)
            session.sendmail(LIFEGUARD_EMAIL_SMTP_USER, emails, message.render())
            session.quit()
        except:
            logger.error(
                "error on send email %s to %s",
                message.render(),
                emails,
                extra={"traceback": traceback.format_exc()},
            )
