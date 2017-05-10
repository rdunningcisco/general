"""
Provides tools for multithreading.

Provided Classes
----------------

RepeatingCaller
    Repeats a function call with each call in a separate thread.

"""

import logging
import os
import threading
from logging.handlers import RotatingFileHandler

import __main__

from library_tools import ConfigReader


###############################################################################


# noinspection PyArgumentList
class RepeatingCaller(object):

    """
    Repeats a function call with each call executed in a separate thread.

    Attributes:
        _timer (obj): A threading.Timer object.

        interval (str): Interval between calls, in minutes.

        total_cycles (str): Total number of calls to be made.

        function (func): Function to be executed.

        args (list): Function arguments, positional.

        kwargs (list): Function arguments, keyword.

        cycle_count (int): Number of cycles completed.

        is_running (bol): True if the function is executing in a particular
            thread.

    """

    def __init__(self, interval, total_cycles, function, *args, **kwargs):

        """
        Initialize the object.

        Args:
            interval (str): The interval between function calls, in minutes.

            total_cycles (str): The total number of function calls.

            function (func): The function we wish to call.

            *args (list): Function positional arguments.

            **kwargs (list): Function keyword arguments.

        Notes:
            This object is self-starting!
        """

        logger.info("Initializing RepeatingCaller object.")

        self._timer = None
        self.interval = int(interval)  # minutes
        self.total_cycles = total_cycles  # integer count
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.cycle_count = 0
        self.is_running = False
        self.start()  # auto starts!

    def _run(self):

        """
        Calls the function.

        Returns: None.

        """

        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)
        self.cycle_count += 1

        if self.cycle_count == self.total_cycles:
            self.stop()

    def start(self):

        """
        Declare a threading.Timer object and pass in self._run.

        Returns: None.

        """

        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def join(self):

        """
        Join the current thread.

        Returns: None.

        """

        self._timer.join()

    def is_alive(self):

        """
        Queries whether the current thread is still alive.

        Returns: self._timer.isAlive()

        """

        return self._timer.isAlive()

    def stop(self):

        """
        Cancels the current thread.

        Returns: None.

        """

        logger.info("Stopping thread.")
        self._timer.cancel()
        self.is_running = False


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
