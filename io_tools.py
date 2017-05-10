"""
Provides functions to perform standard file operations.

Provided Functions
------------------

find_last_occurrence
    Finds the last occurrence of a word in a file. Intended for use on very
    large files.

get_delimited_data
    Read lines of delimited data into a list of tokenized lists.

get_line_count
    Return the number of lines in a file.

write_delimited_data
    Write lines tokenized data into delimited lines.

write_dictionary_data
    Write nested dictionary contents to a delimited file.

write_dictionaries_to_csv
    Writes a list of dictionaries to a csv file.

"""

import csv
import logging
import mmap
import os
import sys
from logging.handlers import RotatingFileHandler

import __main__

import dictionary_tools
from exceptions_library import CustomExceptionBasic
from library_tools import ConfigReader


###############################################################################


def find_last_occurrence(string, filepath):

    """Find the last occurrence of a word in a file.

    Args:
        string (str): The target string.

        filepath (str): The full path, including the file name.

    Returns:
        A dictionary. Key value is the index number where the beginning target
        string was found, value is the string containing the target
        string, read to the end of the line. If target string is not found,
        return None.

    Reference:
        http://stackoverflow.com/questions/23081898/
        find-the-last-occurrence-of-a-word-in-a-large-file-with-python

    """

    try:
        with open(filepath, mode="r") as f:
            m = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

            #  On a Windows machine, replace prot=mmap.PROT_READ with
            #  access=mmap.ACCESS_READ.

            i = m.rfind(string)

            log_message = ("\n\tfilepath: {0}"
                           "\n\tstring: {1}"
                           "\n\tindex: {2}".format(filepath, string, i))

            logger.info(log_message)

            try:
                m.seek(i)
            except ValueError, e:
                logger.error(e)
                return {i: None}

            line = m.readline()

        return {i: line.strip()}

    except EnvironmentError:
        logger.error("Could not open file.")
        raise IOToolsError("Could not open file {0}.".format(filepath))


def get_delimited_data(filepath, delimiter=","):

    """Read lines from a file.

    Arguments:
        filepath (str): The name of the file (full path).

        delimiter (str): The delimiter character. Optional. Default value
                         is a comma.

    Returns:
        A list of data elements.

    Notes:
       We assume the line consists of a single data token, or a list of
       delimited tokens.

    """

    tokens = []

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except TypeError as e:
        logger.error("TypeError: {0}".format(e))
        return tokens

    for line in lines:
        tokens.extend(line.split(delimiter))

    return tokens


def get_line_count(filepath):

    """Return the number of lines in file filepath.

    Args:
        filepath (str): The name of the file (full path).

    Returns: An integer count of the number of lines in the file.

    Notes:
        If the file does not exist, returns -1.

    """

    try:
        with open(filepath, "r") as f:
            i = 0
            for i, l in enumerate(f, 1):
                pass
    except IOError:
        i = -1

    return i


def user_confirm(message):

    """Waits for the user to press enter.

    Arguments:
        message (str): A message to print to the screen.

    """

    #  Make sure stdout and stderr are directed to the screen instead of to
    #  a log file.

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    answer = None

    print "\n\n******* PLEASE CONFIRM *******\n\n"
    print "{0}".format(message)

    instruction = "*** 'c' to continue ***\n*** 's' to stop ***\n"
    answered = False

    while not answered:
        print "Do you wish to continue or stop?\n\n"
        answer = raw_input(instruction).lower()
        answered = answer in ["s", "c"]

    if answer == 'c':
        print "\n\n *** Continuing ***\n\n"
        return

    elif answer == 's':
        print "\n\n *** Shutting down ***\n\n"
        sys.exit(0)


def write_delimited_data(filepath, tokens_list, delimiter=",", mode="a"):

    """Writes the contents of tokens_lists as delimited data.

    Arguments:
        filepath (str): The name of the file (full path).

        tokens_list (list): A list of lists of tokens.

        delimiter (str): Delimiter. Optional. Default value is ",".

        mode (str): Write mode. Optional. Default value is "a".

    """

    try:
        with open(filepath, mode) as f:
            for t_list in tokens_list:
                if isinstance(t_list, basestring):
                    line = t_list
                else:
                    line = delimiter.join([(str(t) if t is not None else "")
                                           for t in t_list])
                f.write("{0}\n".format(line))

    except TypeError as e:
        logger.error("TypeError: {0}".format(e))
        return tokens_list


def write_dictionary_data(filepath, outer_dict, primary_header, delimiter=",",
                          mode="a"):

    """Write dictionary contents (as tokens) to a delimited file.

    Arguments:
        filepath (str): The name of the file (full path).

        outer_dict (dict): The outer dictionary with keys mapped to 
                           an inner dictionary.

        primary_header (str): The header that goes with the the outer
                              dictionary key. The inner dictionary
                              keys are used for the other headers.

        delimiter (str): The token delimiter. Optional. Default value is a
                         comma.

        mode (str): Write mode. Optional. Default value is "a".

    Notes:
        This function is intended to work on a dictionary whose keys are
        mapped to dictionaries.

    """

    header_tokens = []

    try:
        with open(filepath, mode) as f:
            for outer_key, inner_dict in outer_dict.iteritems():
                if not header_tokens:
                    header_tokens = [primary_header]
                    header_tokens.extend(inner_dict.keys())
                    f.write(delimiter.join(header_tokens) + "\n")
                tokens = [outer_key.strip()]
                for value in inner_dict.itervalues():
                    tokens.extend([str(value).strip()])
                f.write(delimiter.join(tokens) + "\n")

    except (IOError, AttributeError, TypeError) as e:
        logger.error("IOError, AttributeError, TypeError: {0}".format(e))


def write_dictionaries_to_csv(filepath, dictionaries, mode="a"):

    """Writes a list of dictionaries to a csv file, using the keys as the
    column headers.

    Args:
        filepath (str):  Filename (full path).

        dictionaries (list): A list of dictionaries.

        mode (str): File write mode. Optional. Default value is "a".

    Returns:
        None

    """

    # Gather all unique keys across all the dictionaries.

    fieldnames = dictionary_tools.key_set(dictionaries)

    with open(filepath, mode) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(dict((fn, fn) for fn in fieldnames))
        for dictionary in dictionaries:
            writer.writerow(dictionary)


###############################################################################


class IOToolsError(CustomExceptionBasic):

    """Custom Exception class.

    Attributes:

        message (str): Error message.

    """

    def __init__(self, message=None):

        """Initialize the object.

        Args:
            message (str): Error message.

        """

        self.message = "io_tools error" if message is None else message

        super(IOToolsError, self).__init__(message)

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
