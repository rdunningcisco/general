"""
Provides tools for working with datetime objects.

Provided Functions
-------------------

days_between
    Determines the number of days between two dates.

days_from_today
    Determines how many days between a given date and today's date.

is_today
    Determines if a given date is today's date.

return_datetime
    Returns a datetime object.

same_date
    Determines if two given dates are the same.

"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import __main__
from dateutil import parser

from library_tools import ConfigReader


################################################################################


def days_between(dt_a, dt_b):

    """Return the number of days (as an integer) between two given dates.

    Args:
        dt_a (str/obj): A date, either as a string or a datetime object.

        dt_b (str/obj): A date, either as a string or a datetime object.

    Returns:
        An integer.

    """

    dt_a = (return_datetime(dt_a).replace(tzinfo=None)
            if not isinstance(dt_a, datetime)
            else dt_a)

    dt_b = (return_datetime(dt_b).replace(tzinfo=None)
            if not isinstance(dt_b, datetime)
            else dt_b)

    return abs((dt_a.date() - dt_b.date()).days)


def days_from_today(dt):

    """Returns the number of days (as an integer) between the given date and
    today's date.

    Args:
        dt (str/obj): A date, either as a string or a datetime object.

    Returns:
        An integer.

    """

    return days_between(dt, datetime.now())


def is_today(dt):

    """Returns a boolean.

    Returns True if dt is today's date. Returns False otherwise.

    Args:
        dt (str/obj): A date, either as a string or a datetime object.

    Returns:
        Boolean True if dt is today's date; False otherwise.

    """

    return same_date(dt, datetime.now())


def return_datetime(dt):

    """Returns a datetime object.

    Args:
        dt (str/obj): A string containing the date and time,
                           or a datetime object.

    Returns:
        A datetime object, timezone naive.

    """

    return parser.parse(dt, fuzzy=True) if not isinstance(dt, datetime) else dt


def same_date(dt_a, dt_b):

    """Return a boolean.

    Returns True if dt_a and dt_b are the same. Returns False otherwise.

    Args:
        dt_a (str/obj): Date and time, either as a string or a datetime
                             object.

        dt_b (str/obj): Date and time, either as a string or a datetime
                             object.

    Returns:
        Boolean True if dt_a and dt_b are the same; False otherwise.

    """

    dt_a = (return_datetime(dt_a).replace(tzinfo=None)
            if not isinstance(dt_a, datetime)
            else dt_a)

    dt_b = (return_datetime(dt_b).replace(tzinfo=None)
            if not isinstance(dt_b, datetime)
            else dt_b)

    return days_between(dt_a, dt_b) == 0

################################################################################

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

################################################################################
# END FILE
