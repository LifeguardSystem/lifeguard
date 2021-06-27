"""
Lifeguard Context Implementation
"""


class LifeguardContext:
    """
    Lifeguard Context
    """

    def __init__(self):
        self._users = []
        self._auth_method = None
        self._only_settings = False
        self._alert_email_template = """From: [[SMTP_USER]]
To: [[RECEIVERS]]
MIME-Version: 1.0
Content-type: text/html
Subject: [[SUBJECT]]

<h1>Validation details</h1>

<quote>
[[MESSAGE]]
</quote>

<hr/>
<p>
    See more details in Lifeguard Dashboard: [[LIFEGUARD_PUBLIC_ADDRESS]].
</p>
"""

    @property
    def only_settings(self):
        """
        Getter for only settings
        """
        return self._only_settings

    @only_settings.setter
    def only_settings(self, value):
        """
        Setter for only settings
        """
        self._only_settings = value

    @property
    def alert_email_template(self):
        """
        Getter for email template
        """
        return self._alert_email_template

    @alert_email_template.setter
    def alert_email_template(self, value):
        """
        Setter for alert email template
        """
        self._alert_email_template = value

    @property
    def auth_method(self):
        """
        Getter for auth method
        """
        return self._auth_method

    @auth_method.setter
    def auth_method(self, value):
        """
        Setter for auth method
        """
        self._auth_method = value

    @property
    def users(self):
        """
        Getter for users
        """
        return self._users

    @users.setter
    def users(self, value):
        """
        Setter for users
        """
        self._users = value

    def valid_user(self, username, password):
        """
        Check if user is valid
        """
        return [
            user
            for user in self.users
            if user["username"] == username and user["password"] == password
        ]


LIFEGUARD_CONTEXT = LifeguardContext()
