"""
This module provides several classes to facilitate logging functionality
for stand-alone scripts via a global logging object that writes to a file named 
after the executing script.

Basic usage:

(1) In any script or module, import this module:

     import logging_tools

(2) Create a local reference to the global LOG object provided by this module:

     LOG = logging_tools.LOG

(3) Create log messages as follows:

     LOG.info("A message with no placeholders.")

     LOG.info("A message with formatting placeholders, {0}, {1}", var_1, var_2)

     You must provide formatting placeholders for each variable passed as an
     argument. Proper formatting will occur behind the scenes (i.e., the string
     format method is NOT required for strings passed to the LOG object).

(4) By default stdout and stderr are directed to the log file. To turn this
    off:

    sys.stdout.active = FALSE  # Does NOT send stdout to the screen.
    sys.stderr.active = FALSE  # Does NOT send stderr to the screen.

    To turn back on:

    sys.stdout.active = TRUE
    sys.stdout.active = TRUE

    Note: Turning off the redirect to log does not send stdout and stderr
    messages to the screen. This can make errors particularly difficult to
    locate. Proceed with caution.

(5) To redirect stdout and stderr to the screen:

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    To redirect stdout and stderr back to the log file:

    sys.stdout = _StreamToLOG(LOG, logging.INFO)
    sys.stderr = _StreamToLOG(LOG, logging.ERROR)

Provided Classes
----------------

_LoggerManager
     A singleton base class that creates and returns a logging object.

_NewStyleLogMessage:
     A class to provide lazy formatting of strings for log messages.

_LogWriter
     A wrapper class that writes message to the log file.

_StreamToLOG:
     A class to redirect stdout and stderr message to the log file.

"""

import inspect
import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler

import __main__

from library_tools import ConfigReader
from library_tools import Singleton


###############################################################################


def get_log_location():

    """Retrieves the "address" of a log statement in the code.

    Returns:
        A dictionary with keys "class", "function", "line_number", "filepath".

    Notes:
        "class": Name of the class.
        "function": Name of the function or class method.
        "line_number": Line number of the first line of the function.
        "filepath": file path for the file containing the class or function.

    """

    p_frame = None

    for item in inspect.stack():
        if item[1] not in __file__.rstrip('cd'):
            p_frame = item[0]
            break

    location = {}

    if "self" in p_frame.f_locals.keys():
        location["class"] = p_frame.f_locals["self"].__class__.__name__
    else:
        location["class"] = ""

    location["function"] = p_frame.f_code.co_name
    location["line_number"] = p_frame.f_code.co_firstlineno
    location["filepath"] = p_frame.f_code.co_filename.split("/")[-1]

    del p_frame

    return location


###############################################################################


class _LoggerManager(object):

    """Creates and initializes a logging object.

    This object is intended to handle logging for stand-along scripts and 
    supporting modules-- that is, any script or module that imports the 
    global instance of the _LogWriter class declared at the bottom of this 
    file. That instance will have a attribute "log" which is mapped to a 
    logger instance returned by this class' get_logger method.

    The effect of this class is to return a logger instance that is dedicated
    to a specific script.

    """

    __metaclass__ = Singleton

    _loggers = {}

    def __init__(self, *args, **kwargs):

        pass

    @staticmethod
    def get_logger(log_filename=None):

        """Create a Logger object.

           Args:
               log_filename (str): Filename for the log file.

           Notes:
               Log files are stored in a subdirectory of the directory that
               contains this module. The subdirectory is created if it does
               not already exist. If it cannot be created, log files are
               written to the local directory.

               Several local parameters are mapped to module parameters which
               are defined at the bottom of the file. For example,

               log_dir = module_log_directory

               ensures that the directory for the script log file is the same as
               the directory for the module log file. The later is harvested
               from the logging.cfg file.

        """

        log_filename = "log.log" if log_filename is None else log_filename

        log_asctime_format = module_log_asctime_format
        log_dir = module_log_directory
        log_format = module_log_config.get_item("logging", "script_log_format")
        log_level = module_log_level
        log_level_map = module_log_level_map
        log_max_bytes = module_log_max_bytes
        log_backup_count = module_log_backup_count

        if not os.path.isdir(log_dir):

            try:
                os.makedirs(log_dir)

            except OSError as e:
                print "WARNING: Could not create LOGS directory."
                print e

                # Set the log directory to a convenient default directory.
                # Change this as necessary depending on the system.

                log_dir = "/logs"

        log_filepath = "{0}/{1}".format(log_dir, log_filename)

        if os.path.isfile(log_filepath):

            with open(log_filepath, "a") as f:
                f.write("\n--------------------------------------------------")
                f.write("\n\n")

        log_formatter = logging.Formatter(log_format, log_asctime_format)
        log_handler = RotatingFileHandler(log_filepath, maxBytes=log_max_bytes,
                                          backupCount=log_backup_count)
        log_handler.setFormatter(log_formatter)

        _LoggerManager._loggers[log_filename] = logging.getLogger(log_filepath)
        _LoggerManager._loggers[log_filename].setLevel(log_level_map[log_level])
        _LoggerManager._loggers[log_filename].addHandler(log_handler)

        module_logger.info("Returning logger: {0}".format(log_filename))

        return _LoggerManager._loggers[log_filename]

###############################################################################


class _LogWriter(object):

    """A wrapper class to write messages to the log file.

    Attributes:
        log (obj): An instance of the Python logger class.

        nslm (obj): An instance of _NewStyleLogMessage.

    """

    def __getattr__(self, name):

        """Overriding __getattr__.

        Arguments:
            name (str): An attribute name for this class.

        Returns:
            catch (def): returns self.warning.

        Notes:
            The point here is to gracefully catch attempts to write
            to the log file at an invalid level (something other than
            debug, info, warning, error, or critical). If an invalid
            level is specified, we log the catch, and write the message
            at warning level.

        """

        def catch(*args):
            """Catch an invalid logging level.

            Arguments:
                args (tuple): The message string plus optional parameters.

            """

            if name not in self.log_levels:
                message = ("Caught invalid log level {0}. Writing to "
                           "warning level instead.".format(name.upper()))

                self.warning(message)
                self.warning(*args)  # Why a separate call?

        return catch

    def __init__(self, caller=None):

        """Initialize the object.

        Arguments:
            caller (str): The name of calling script. Optional. Default value is
                          None.

        Notes:
            After initialization, an instance of this class will have an
            attribute self.log which maps to logger instance returned by
            _LoggingManager.get_logger().

            The primary point of this class is to pass all logging messages
            through an instance of _NewStyleLogMessage. Some additional
            control is also gained, such as directing all stdout/stderr
            messages to the script log file.

        """

        if not caller:
            if "/" in sys.argv[0]:
                caller = sys.argv[0].split("/")[-1]
            elif "\\" in sys.argv[0]:
                caller = sys.argv[0].split("\\")[-1]
            else:
                caller = sys.argv[0]

        caller_extension = os.path.splitext(caller)[1]
        log_extension = module_log_extension
        log_file = caller.replace(caller_extension, log_extension)
        self.log = _LoggerManager().get_logger(log_file)
        self.call_map = {"debug": self.log.debug, "info": self.log.info,
                         "warning": self.log.warning,
                         "error": self.log.error,
                         "critical": self.log.critical}
        self.nslm = _NewStyleLogMessage
        sys.stdout = _StreamToLOG(self.log, logging.INFO)
        sys.stderr = _StreamToLOG(self.log, logging.ERROR)

    def record_user_options(self, options):

        """Writes the command line options provided by the user or by a
        trigger. Assumes that we are using optparse to gather command-line
        arguments.

        Args:
            options (obj): An optparse.Values instance.

        """

        options_message = "Options:"

        for option, value in options.__dict__.items():
            r_value = value if option != "password" else "************"
            options_message += "\n\toption: {0}; value: {1}".format(option,
                                                                    r_value)

        self.info(options_message)

    def debug(self, message, *args):

        """Write a message to the log file at debug level.

        Arguments:
            message (str): message string.

            args (list): optional arguments parsed into the message string.

        """

        message = str(message) if type(message) is list else message

        self.write_to_log("debug", message, *args)

    def info(self, message, *args):

        """Write a message to the log file at info level.

        Arguments:
            message (str): message string.

            args (list): optional arguments parsed into the message string.

        """

        message = str(message) if type(message) is list else message

        self.write_to_log("info", message, *args)

    def warning(self, message, *args):

        """Write a message to the log file at warning level.

        Arguments:
            message (str): message string.

            args (list): optional arguments parsed into the message string.

        """

        message = str(message) if type(message) is list else message

        self.write_to_log("warning", message, *args)

    def error(self, message, *args):

        """Write a message to the log file at error level.

        Arguments:
            message (str): message string.

            args (list): optional arguments parsed into the message string.

        """

        message = str(message) if type(message) is list else message

        self.write_to_log("error", message, *args)

    def critical(self, message, *args):

        """Write a message to the log file at critical level.

        Arguments:
            message (str): message string.

            args (list): optional arguments parsed into the message string.

        """

        message = str(message) if type(message) is list else message

        self.write_to_log("critical", message, *args)

    def log_warning(self, message):

        """Write a warning message to the log file.

        Arguments:
            message (str): message string.

        Notes:
            This function does not pass message to the _NewStyleLogMessage
            class, specifically because messages written to the log file from
            that class use this function.

            This function is intended to cite log messages that have some
            type of formatting error.

        """

        self.log.warning(message)

    def status(self, message):

        """Prints a status message to stdout.

        """

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        print message

        sys.stdout = _StreamToLOG(self.log, logging.INFO)
        sys.stderr = _StreamToLOG(self.log, logging.ERROR)

    def write_to_log(self, level, message, *args):

        """Writes a message to the log file at the given level.

        Arguments:
            message (str): message string.

            level (str): logging level.

        """

        level = level.lower()
        location = get_log_location()

        if location["function"] == "main":
            full_message = "{0}:{1}".format(location["filepath"], message,
                                            *args)
        else:
            full_message = "{0}:{1}:{2}".format(location["class"],
                                                location["function"], message)

        message_to_log = self.nslm(full_message, *args)
        self.call_map[level](message_to_log, exc_info=level in ["critical",
                                                                "error"])

###############################################################################


class _NewStyleLogMessage(object):

    """Formats strings.

    Formats log messages; allow for lazy formatting.

    Attributes:
        message (str): The message to be written to the log file.

        args (variable): Variables formated for the message string.

        kwargs (variable): keyword arguments.

    Notes:
        All messages sent to the logger object may be passed through an
        instance of this class, although this is not strictly required.

        For example, if nslm is an instance of this class:

        log(nslm("This is a log message.", variable))

        If not using nslm, format the log message as follows:

        log("This is a log message.".format(variable))

    """

    def __init__(self, message, *args, **kwargs):

        """Initialize the class object.

        Args:
            message (str): The message to be written to the log file.

            args (variable): Variables formatted for the message string.

            kwargs (variable): keyword arguments.

        Notes:
            A formatting error in a log statement will generate a
            stdout/stderr message that needs to be caught and logged by a
            function that DOES NOT call __str__, otherwise we will generate
            an infinite recursion. We handle this below by calling
            log.log_warning in the event of an exception.

        """

        self.message = message
        self.args = args
        self.kwargs = kwargs

    def __str__(self):

        """Return a formatted message string.

        """

        args = (i if type(i) is type else i() if callable(i)
                else i for i in self.args)

        kwargs = dict((k, v() if callable(v) else v)
                      for k, v in self.kwargs.items())

        try:
            return self.message.format(*args, **kwargs)
        except IndexError:
            log.log_warning("A log statement is missing a format argument. "
                            "\n\tLine to log was: {0}".format(self.message))
            log.log_warning("args: {0}".format(args))
            log.log_warning("kwargs: {0}".format(kwargs))
            return "...... (Index) A log statement contained an error ......"
        except ValueError:
            log.log_warning("A log statement has a syntax error."
                            "\n\tLine to log was: {0}".format(self.message))
            return "...... (Value) A log statement contained an error ......"
        except TypeError:
            log.log_warning("A log statement has a type error."
                            "\n\tLine to log was: {0}".format(self.message))
            return "...... (Type) A log statement contained an error ......"


###############################################################################


class _StreamToLOG(object):

    """Redirect stdout and stderr to the log file.

    Attributes:
        logger (obj): A python Logger object.

        level (int): The level of the log message, either INFO, ERROR, etc.

    """

    def __init__(self, logger, level):

        """Initialize the class object.

        Set instance variable active to False to suppress stdout or stderr
        output. This does NOT redirect that output to the screen.

        Args:
            logger (obj): A python Logger object.

            level (int): The level of the log message, either INFO, ERROR, etc.

        """

        self.active = True  # Set to False to suppress.
        self.caller = None
        self.logger = logger
        self.level = level

    def turn_off(self):
        self.active = False

    def turn_on(self):
        self.active = True

    def toggle(self):
        self.active = not self.active

    def write(self, message):

        """Write the stream message to the log file.

        Args:
            message (str): The stream message from stdout or stderr.

        """

        if not self.active:
            return

        # Wrap everything in try/except to catch errors that
        # otherwise would be invisible.

        # Need to parse messages based on self.level. Info messages should
        # be printed differently from ERROR messages.

        try:
            if message != '\n':

                if self.caller is not None:
                    message = "STREAM: {0}".format(self.caller + message)
                else:
                    message = "STREAM: {0}".format(message)

                self.logger.log(self.level, message)

        except Exception as e:

            # Must catch ALL exceptions!!
            #
            # Unset stdout and stderr redirect, else any errors in this
            # function will not be reported anywhere-- making them very,
            # very difficult to find.

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            print "TRACEBACK: {0}".format(traceback.extract_stack())
            print "message is {0}".format(message)
            print "error is {0}".format(e)
            print "Fatal ERROR redirecting stdout, stderr to log. STOPPING."
            raise SystemExit


###############################################################################


# Set up logging for this module.

module_log_level_map = {"critical": logging.CRITICAL, "error": logging.ERROR,
                        "warning": logging.WARNING, "info": logging.INFO,
                        "debug": logging.DEBUG, "notset": logging.NOTSET}

base_path = os.path.dirname(os.path.realpath(__file__))
module_logger_name = __name__
module_logger = logging.getLogger(module_logger_name)
module_log_config = ConfigReader(os.path.join(base_path, r"logging.cfg"))
module_log_asctime_format = module_log_config.get_item("logging",
                                                       "asctime_format")
module_log_backup_count = module_log_config.get_item("logging",
                                                     "log_backup_count")
module_log_directory = module_log_config.get_item("logging", "log_directory")
module_log_format = module_log_config.get_item("logging", "module_log_format")
module_log_extension = module_log_config.get_item("logging", "log_extension")
module_log_level = module_log_config.get_item("logging", "log_level")
module_log_max_bytes = module_log_config.get_item("logging", "log_max_bytes")
module_log_filename = "{0}{1}".format(module_logger_name, module_log_extension)
module_log_filepath = "{0}/{1}".format(module_log_directory,
                                       module_log_filename)
module_log_formatter = logging.Formatter(module_log_format,
                                         module_log_asctime_format)
module_log_handler = RotatingFileHandler(module_log_filepath,
                                         maxBytes=module_log_max_bytes,
                                         backupCount=module_log_backup_count)
module_log_handler.setFormatter(module_log_formatter)
module_logger.setLevel(module_log_level_map[module_log_level])
module_logger.addHandler(module_log_handler)
module_logger.info("--------------------------------------------------------\n")
module_logger.info("**** Imported by {0} ****".format(__main__.__file__))

# Global log object is intended for stand-alone scripts and supporting modules.

log = _LogWriter()

###############################################################################
# END FILE
