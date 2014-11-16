import logging, logging.config
import smtplib
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.plugins.notifications.mailer.manager import MailManager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


class MailClient():
    def __init__(self, view_name):
        self.CONFIG = None
        self.validated = False
        self.connected = False
        self.error = None
        mail_manager = MailManager(view_name)
        self.config = mail_manager.config
        self.config_exists = False
        if self.config.server:
            self.config_exists = True

    def server_status(self):
        msg = ''
        try:
            ehlo = self.mail.ehlo()
            if ehlo[0] == 250:
                self.connected = True

            self.server_reply_code = ehlo[0]
            self.server_reply_message = ehlo[1]
            msg = self.server_reply_message
            logger.info(msg)

        except Exception as e:
            msg = (
                'Connection to mail server {0} has not been initialized: {1}'
                .format(self.config.server, e)
            )
            logger.exception(msg)

        return(msg)

    def connect(self):
        connected = False
        logged_in = False
        msg = None
        mail = None
        try:
            if self.config.is_ssl:
                mail = (
                    smtplib.SMTP_SSL(
                        self.config.server, self.config.port, timeout=10
                    )
                )

            else:
                mail = (
                    smtplib.SMTP(self.config.server, self.port, timeout=10)
                )

            connected = True
            msg = 'Connected to {0}'.format(self.config.server)

        except Exception as e:
            logger.exception(e)
            msg = 'Failed to Connect to {0}'.format(self.config.server)

        if connected:
            try:
                if self.config.is_tls:
                    mail.starttls()
                mail.login(self.config.username, self.config.password)
                logged_in = True
                msg = 'Successfully logged into {0}'.format(self.config.server)

            except Exception as e:
                logger.exception(e)
                msg = 'Failed to log into {0}'.format(self.config.server)

        self.connected = connected
        self.error = msg
        self.logged_in = logged_in
        self.mail = mail

        return(connected, msg, logged_in, mail)

    def disconnect(self):
        msg = ''
        self.disconnected = False
        try:
            loggedout = self.mail.quit()
            msg = (
                'Logged out of Email Server {0}: {1}'
                .format(self.config.server, loggedout)
            )
            self.disconnected = True
            logger.info(msg)

        except Exception as e:
            msg = (
                'Failed to log out of {0}: {1}'
                .format(self.config.server, e)
            )
            self.disconnected = True
            logger.exception(e)

        return(self.disconnected, msg)

    def send(self, subject, msg_body, to_addresses=None, body_type='html'):
        completed = True

        if not to_addresses:
            to_addresses = [self.config.to_email]

        if isinstance(to_addresses, list):
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.from_email
            msg['To'] = ','.join(to_addresses)
            msg['Subject'] = subject
            formatted_body = MIMEText(msg_body, body_type)
            msg.attach(formatted_body)
            try:
                self.mail.sendmail(
                    self.config.from_email,
                    to_addresses,
                    msg.as_string()
                )
            except Exception as e:
                completed = False
                msg = (
                    'Could not send mail to {0}: {1}'.
                    format(','.join(to_addresses), e)
                )
                logger.exception(msg)


        return completed
