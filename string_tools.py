"""
Provides functions to manipulate strings.

Provided Functions
------------------

batch_replace
    Replace all occurances of a substring in a string.

check_types
    Checks that variables of a particular type.

clean_line
    Cleans escape and other special characters from a line.

compress_delimiter (NOT WORKING AS INTENDED)
    Removes delimiter character from within specific tokens in delimited string
    (i.e., compresses certain adjacent tokens into a single token).

exact_match
    Returns True if input string is an exact match to comparison string or to
    any member of a list of comparison strings.

modify_tokens
    Modifies specific tokens in a delimited string, or reverses the
    modification to return the original delimited string.

remove_tokens
    Removes specific tokens from a delimited string.

replace_last
    Replace the last occurance of a substring in a string.

strip_last_parentheses
    Strips away last text in string that is inside parentheses.

strip_non_alphanumeric
    Remove all non-alphanumeric characters from a string.

strip_tokens
    Strips whitespace from a list of tokens.

tokenize
    Converts a delimited string into a list of tokens.

"""

import csv
import logging
import os
import re
import sre_constants
from cStringIO import StringIO
from logging.handlers import RotatingFileHandler

import __main__

from library_tools import ConfigReader


###############################################################################


def batch_replace(source_string, old_subs, new_subs):

    """Swap elements in old_subs for matching elements in new_subs.

       Arguments:
           source_string (str): The source string.

           old_subs (list): A list of target substrings to replace.

           new_subs (list): A list of new substrings to insert.

       Notes:
           Each item in old_subs is replaced by the corresponding item in
           new_subs. Both lists must be of the same length.

    """

    old_subs = [old_subs] if not isinstance(old_subs, list) else old_subs
    new_subs = [new_subs] if not isinstance(new_subs, list) else new_subs
    new_string = None

    if len(old_subs) != len(new_subs):
        print "{0}: Lists must be of the same length.".format(__file__)
        return source_string

    for o, n in zip(old_subs, new_subs):
        try:
            new_string = source_string.replace(o, n)
        except AttributeError as e:
            print "{0}: {1}".format(__file__, e)
            return source_string

    return new_string


def check_types(list_, type_):

    """Return a boolean.

    Checks that list_ or all members of list_ are of type type_.

    """

    list_ = [list_] if not isinstance(list_, list) else list_
    check_list = []

    for i in list_:
        if isinstance(i, list):
            check_list.extend(i)
        else:
            check_list.append(i)

    return all(isinstance(i, type_) for i in check_list)


def clean_line(line):

    """
    Cleans escape and other characters that often show up in text captured
    from stdout.

    Args:
        line (str): A line to be cleaned.

    Returns: A string-- the cleaned line.

    """

    escapes = ''.join([chr(char) for char in range(1, 32)])
    prep_line = re.compile(r'\x1b[^m]*m').sub('', line)
    return prep_line.translate(None, escapes)


def compress_commas(text):

    """Compress comma-separated elements.

    Arguments:
        text (str): String text.

    Returns:
        (str) : comma-deliminated string, where commas in the original
                elements have been suppressed.

    Note:
        New line characters are preserved.

    Example:
        "a, b, 'c,d', e" returns "a, b, cd, e".

    """

    file_like_object = StringIO("\n".join("".join(line.split())
                                for line in text.split("\n")))

    return [r for r in csv.reader(file_like_object, quotechar="'")]


def exact_match(string, comp):

    """Return a boolean.

       Determines if string is an exact match to comparison, or to
       any member of comparison if comparison is a list.

       Arguments:
           string (str): The string you're checking.

           comp (str/list): Either a string or a list of strings.

    """

    comp = [comp] if not isinstance(comp, list) else comp

    results = []

    for item in comp:
        try:
            results.extend(re.findall("\\{0}\\b".format(string), item))
        except sre_constants.error as e:
            print "{0}: {1}".format(__file__, e)
            return False

    if results:
        return True
    else:
        return False


def modify_tokens(lines, replacement_map, targets, action, delimiter=","):

    """Return a list.

       Applies or undoes the action of replacement_map to the target
       tokens in a list of lines with delimited values.

       The intended use here is for cases where specific tokens need to
       be modified prior to sorting, and then changed back to their
       original values. In normal usage this function will be called
       twice-- once before the sorting procedure is invoked, and once
       afterward.

       Arguments:
           lines (list): A list of lines with delimited values.

           replacement_map (dict): A map of original target tokens to
               replacement target tokens.

           targets (list): The index numbers of the target tokens.

           action (str): Either "do" or "undo."

           delimiter (str): Token delimiter. Optional. Default value is ",".

    """

    if not check_types(replacement_map, dict):
        print ("{0}: Replacement_map argument must be of type dict."
               .format(__file__))
        logger.error("{0}: Replacement_map argument must be of type dict."
                     .format(__file__))
        return lines

    targets = [targets] if not isinstance(targets, list) else targets

    action = action.lower()

    if action not in ["undo", "do"]:
        print ("action argument must be of value \"do\" or \"undo\". "
               "Received {0} instead.", action)
        logger.error("action argument must be of value \"do\" or \"undo\". "
                     "Received {0} instead.", action)
        return lines

    new_lines = []

    for line in lines:
        tokens = tokenize(line)

        if action == "do":
            for target in targets:
                tokens[target] = replacement_map[tokens[target]]

        elif action == "undo":
            for key in replacement_map:
                for target in targets:
                    if replacement_map[key] == tokens[target]:
                        tokens[target] = key

        line = delimiter.join(tokens)
        new_lines.append(line)

    return new_lines


def replace_last(source_string, old_sub, new_sub):

    """Search for substring old_sub in source_string
       starting at the end. Replace the first occurrence of
       old_sub with new_sub.

       Returns the new string.

    """

    try:
        head, sep, tail = source_string.rpartition(old_sub)
    except AttributeError as e:
        print "{0}: {1}".format(__file__, e)
        return source_string

    return head + new_sub + tail


def remove_tokens(string, targets, delimiter=","):

    """Return a string.

       The action depends on targets. If targets is a list of strings, this
       function removes the matching tokens from the input string. If
       targets is a list of integers, it removes tokens at those index
       positions from the input string.

       Arguments:
           string (str): Target string.

           targets (list): List of target tokens to be removed or
                           list of token index positions to be
                           removed.

           delimiter (str): String delimiter. Optional. Default value is ",".
    """

    if not check_types(string, basestring):
        print "First argument must be of type str."
        logger.error("First argument must be of type str.")
        return string

    if check_types(targets, basestring):
        targets = strip_tokens(targets)
        tokens = tokenize(string)
        return delimiter.join([t for t in tokens if t not in targets])

    elif check_types(targets, int):
        tokens = tokenize(string)
        return delimiter.join([tokens[i] for i in xrange(len(tokens))
                               if i not in targets])
    else:
        print ("The elemets of the targets list must all be of type "
               "str or type int.")
        logger.error("The elements of the targets list must all be of type "
                     "str or type int.")

        return string


def strip_last_parentheses(string):

    """Strip from string the final occurrence of text within parentheses.

    Arguments:
        string (str): String.

    Example:
        string = "example string (abc) with parentheses (def)"

        return: "example string (abc) with parentheses"

    """

    if string.find("(") > -1 and string.find(")") > -1:
        return re.sub('(.*)(\(.*\))', '\\1', string)
    else:
        return string


def strip_non_alphanumeric(source_string):

    """Strip all non-alphanumeric characters from source string.

       Returns:
           A string containing only the alphanumeric characters in
           source_string.

        """

    non_alphanum = ''.join(c for c in map(chr, range(256))
                           if not c.isalnum())

    try:
        new_string = source_string.translate(None, non_alphanum)
    except TypeError:
        temp_string = source_string.encode("ascii", "ignore")
        new_string = temp_string.translate(None, non_alphanum)
    except AttributeError as e:
        print "{0}: {1}".format(__file__, e)
        return source_string

    return new_string


def strip_tokens(tokens):

    """Return a list of tokens with whitespace stripped.

    """

    try:
        return [t.strip() for t in tokens]
    except AttributeError as e:
        print "{0}: {1}".format(__file__, e)
        return tokens


def tokenize(string, delimiter=","):

    """Return a list of tokens.

       Splits delimited string into tokens.

       Arguments:
           string (str): A string of delimited tokens.

           delimiter (str): A delimiter. Optional. Default is ",".

    """

    try:
        return strip_tokens(string.split(delimiter))
    except AttributeError as e:
        print "{0}:{1}".format(__file__, e)
        return string

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
