"""
Provides functions and classes for various systems operations.

Provided Functions
------------------
system_command
    Executes a file system command.

Provided Classes
------------------

TopData
    Exports data from the unix top command to a file.

"""

import datetime
import logging
import os
import subprocess
from logging.handlers import RotatingFileHandler

import __main__

import string_tools
from library_tools import ConfigReader


###############################################################################


def system_command(cmd):

    """Excute a system command.

    Args:
        cmd (str): A command-line string.

    Excutes a Linux command-line instruction.

    Raises:
        OSError: The command did not execute.

    Returns:
        True: successful execution.

        False: unsuccessful execution.

    """

    command_tokens = [i for i in cmd.split()]

    debug_system_calls = False  # Set to True to debug system calls

    try:

        if not debug_system_calls:
            subprocess.call(command_tokens)
        else:
            p = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
            out, err = p.communicate()
            logger.debug("command: {0}".format(" ".join(command_tokens)))
            logger.debug("out: {0}".format(out))
            logger.debug("err: {0}".format(err))

    except OSError as e:
        logger.error("OSError: {0}".format(e))
        return False

    return True


class TopData(object):

    def __init__(self, filename=None, user_ids=None, process_names=None,
                 column_indexes=None):

        """

        Initialize the object.

        Args:
            filename (str): The name of the output file. Optional. Default
                value is None.

            user_ids (list): System user IDs. Optional. Default value is None.

            process_names (list): Process names. Optional. Default value is an
                empty list.

            column_indexes (list): The index numbers for the data columns that
                we wish to capture.
        """

        if column_indexes is None:
            column_indexes = []
        if process_names is None:
            process_names = []
        if user_ids is None:
            user_ids = []
        if filename is None:
            now = datetime.datetime.now()
            current_date = datetime.datetime.strftime(now, "%H%M%S_%m%d%Y")
            self.filename = "topdata_{0}.txt".format(current_date)
        else:
            self.filename = filename

        self.user_ids = user_ids
        self.process_names = process_names
        self.temp_file = "./DATA/top_data_temp.csv"

        # The following sets the column numbers that we wish to capture.

        if not column_indexes:
            self.column_indexes = [1, 4, 8, 9, 10, 11]
        else:
            self.column_indexes = column_indexes

    def capture_top_data(self, refresh_cycles="1"):

        """
        Capture output data from the unix top command.

        Args:
            refresh_cycles (str): Number of refresh cycles for top. Optional.
                Default value is 1.

        Returns: None.

        """

        top_call = ["top", "-n", refresh_cycles, "-a", "-M", "-m", "-H", "-S",
                    "-u", self.user_ids[0]]

        with open(self.filename, "a") as f:
            subprocess.call(top_call, stdout=f)

    def parse_top_data(self):

        """
        Parses output data captured from the top command.

        Returns: None.

        """

        def write_line_to_file(line, f):
            column_indexes = self.column_indexes
            cleaned_line = string_tools.clean_line(line)
            tokens = string_tools.tokenize(cleaned_line, None)
            delimited_string = ",".join(map(tokens.__getitem__, column_indexes))
            f.write(delimited_string + "\n")

        captured_header = False
        header_clue = "TIME+"
        user_id = self.user_ids[0]
        process_names = self.process_names

        with open(self.filename, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()  # Erases all data in the file.

        #  Create a separate output file for each parameter specified by
        #  by the user.

            for line in lines:

                if not captured_header and header_clue in line:
                    write_line_to_file(line, f)
                    captured_header = True

                elif process_names and all(p not in line
                                           for p in process_names):
                    continue

                elif user_id not in line:
                    continue

                else:
                    write_line_to_file(line, f)


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
