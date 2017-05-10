"""
Provides a function to send email messages.

Provided Functions
------------------

send_email
    Sends an email message.

Provided Classes
----------------

EmailToolsError
    Custom exception class.

"""

import logging
import os
import smtplib
from email import Encoders
from logging.handlers import RotatingFileHandler

import __main__
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import html_tools
from exceptions_library import CustomExceptionBasic
from library_tools import ConfigReader


###############################################################################


def generate_support_email(sbj=None, msg=None):

    """Generates an email to person responsible for support.

    Args:

        sbj (str): Email subject. Optional. Default value is None.

        msg (str): Error message. Optional. Default value is None.

    Returns:

        None.

    """

    sbj = "Python Script Error" if sbj is None else sbj
    msg = "Check logs and system status!!" if msg is None else msg

    send_email(subject=sbj, message=msg)


def send_email(**kwargs):

    """Send an email message.

    Args:
        kwargs: subject -- subject line for the email (default None)
        recipients -- a list of recipients (default empty)
        files -- a list of files to attach (default empty)
        message -- the message text (default None)
        mimetype -- the MIME type (default plain)

    Raises:
        Exception: a general error exception has occurred.

    Returns:
        True: email was successfully sent.

        False: email was not successfully sent.

   """

    subject = None
    recipients = []
    files = []
    message = None
    mimetype = "plain"  # default

    for key, value in kwargs.iteritems():
        if key.lower() == "subject":
            subject = value
        elif key.lower() == "recipients":
            recipients = value
        elif key.lower() == "files":
            files = value
        elif key.lower() == "message":
            message = value
            message = message.encode("utf-8", "replace")
        elif key.lower() == "mimetype":
            mimetype = value

    log_info = ("Email info:"
                "\n\tsubject: {0}"
                "\n\trecipients: {1}"
                "\n\tfiles: {2}"
                "\n\tmimetype: {3}".format(subject, recipients, files,
                                           mimetype))

    logger.info("{0}".format(log_info))

    config = ConfigReader("/cfg/cfg.cfg")
    email_address = config.get_item("support", "system_email")
    support_lead = config.get_item("support", "support_lead")
    support_email = config.get_item("support", "support_email")
    salutation = ("\n\nPlease do not respond to this message, as it "
                  "was sent from an unmonitored account. For "
                  "technical support, please contact {0} at {1}.\n\n"
                  "Thank you.".format(support_lead, support_email))

    if message is None:
        logger.warning("Message is None. Nothing to send. Returning.")
        return
    else:
        message += salutation

    if mimetype.lower() == "html":
        message = html_tools.create_paragraph(message)

    if subject is None:
        subject = "No Subject."

    if not isinstance(recipients, list):
        if recipients is None:
            recipients = []
        else:
            recipients = [recipients]

    if support_email not in recipients:
        recipients.append(support_email)

    mail_msg = MIMEMultipart('alternative')
    mail_msg["From"] = email_address
    mail_msg["To"] = ", ".join(recipients)
    mail_msg["Subject"] = subject
    mail_msg.attach(MIMEText(message, mimetype))

    for f in files:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        content_string = "Content-Disposition"
        bn = os.path.basename(f)
        attachment_string = "attachment; filepath=\"{0}\"".format(bn)
        part.add_header(content_string, attachment_string)
        mail_msg.attach(part)

    s = smtplib.SMTP("localhost")

    try:

        # Don't use mail_msg["To"] as an argument to sendmail; it is
        # not formatted correctly-- only the first address in the list
        # will receive the message. Use the recipients list instead.

        s.sendmail(mail_msg["From"], recipients, mail_msg.as_string())

    except smtplib.SMTPException as e:
        logger.error("smtplib.SMTPException error: {0}".format(e))
        raise EmailToolsError(e.message)

    s.quit()


###############################################################################


class EmailToolsError(CustomExceptionBasic):

    """Custom Exception class.

    Attributes:

        message (str): Error string.

    """

    def __init__(self, message=None):

        """Initialize the object.

        Args:
            message (str): Error message.

        """

        self.message = "email tools error" if message is None else message

        super(EmailToolsError, self).__init__(message)


###############################################################################


# Set up logging for this module.

log_level_map = {"critical": logging.CRITICAL, "error": logging.ERROR,
                 "warning": logging.WARNING, "info": logging.INFO,
                 "debug": logging.DEBUG, "notset": logging.NOTSET}

base_path = os.path.dirname(os.path.realpath(__file__))
logger_name = __name__
logger = logging.getLogger(logger_name)
log_config = ConfigReader(os.path.join(base_path, r"logging.cfg"))
log_asctime_format = log_config.get_item("logging", "asctime_format")
log_backup_count = log_config.get_item("logging", "log_backup_count")
log_directory = log_config.get_item("logging", "log_directory")
log_format = log_config.get_item("logging", "module_log_format")
log_extension = log_config.get_item("logging", "log_extension")
log_level = log_config.get_item("logging", "log_level")
log_max_bytes = log_config.get_item("logging", "log_max_bytes")
log_filename = "{0}{1}".format(logger_name, log_extension)
log_filepath = "{0}/{1}".format(log_directory, log_filename)
log_formatter = logging.Formatter(log_format, log_asctime_format)
log_handler = RotatingFileHandler(log_filepath, maxBytes=log_max_bytes,
                                  backupCount=log_backup_count)
log_handler.setFormatter(log_formatter)
logger.setLevel(log_level_map[log_level])
logger.addHandler(log_handler)
logger.info("----------------------------------------------------------------")
logger.info("**** Imported by {0} ****".format(__main__.__file__))

# END FILE
