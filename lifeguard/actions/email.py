"""
Action to send problem
"""
import smtplib
import traceback

from lifeguard import PROBLEM
from lifeguard.context import LIFEGUARD_CONTEXT
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.settings import (
    LIFEGUARD_EMAIL_SMTP_PORT,
    LIFEGUARD_EMAIL_SMTP_SERVER,
    LIFEGUARD_EMAIL_SMTP_USER,
    LIFEGUARD_EMAIL_SMTP_PASSWD,
    LIFEGUARD_PUBLIC_ADDRESS,
)


class Message(object):
    """
    Email render template
    """

    def __init__(self, receivers, subject, message, template):
        self.receivers = receivers
        self.subject = subject
        self.message = message
        self.template = template

    def render(self):
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
    if validation_response.status in settings["email"]["send_in"]:

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
