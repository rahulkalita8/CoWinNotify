import os
import smtplib
import base64
import email.message
from configparser import ConfigParser

pwd = os.getcwd()
config = ConfigParser()
config_path = os.path.dirname(os.path.abspath(__file__))
config.read_file(open(os.path.join(config_path, '../resources/configuration.ini')))


class Mail:

    default_smtp_host = "smtp.gmail.com"
    default_smtp_port = 587

    def __init__(self):
        self.username = config.get('mail', 'username') or None
        self.password = config.get('mail', 'password') or None
        self.receivers = config.get('mail', 'receivers') or None
        self.encoded = True
        self.server = None
        self.message = None

    def connect(self, username=None, password=None, smtp_host=default_smtp_host, smtp_port=default_smtp_port, encoded=True):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if encoded:
            password_bytes = base64.b64decode(self.password)
            self.password = password_bytes.decode("ascii")
        self.server = smtplib.SMTP(smtp_host, smtp_port)
        self.server.starttls()
        self.server.login(self.username, self.password)

    def send_mail(self, sender, receivers, subject, body):
        self.create_message(sender, receivers, subject, body)
        self.server.sendmail(sender, receivers, self.message.as_string())

    def create_message(self, sender, receivers, subject, body):
        self.message = email.message.Message()
        self.message['From'] = sender
        self.message['To'] = str(receivers)
        self.message['Subject'] = subject
        self.message.set_payload(body)


