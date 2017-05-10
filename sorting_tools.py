"""
A library of general sorting routines.

Provided Functions
------------------
check_types
    Checks variable types.

natural_sort
    Return a naturally-sorted list.

sort_subsort
    Return a sorted list (with primary and secondary sorting).

quicksort
    The standard QuickSort algorithm.

"""

import logging
import os
import re
from logging.handlers import RotatingFileHandler

import __main__

import string_tools
from dictionary_tools import LastUpdatedOrderedDict
from library_tools import ConfigReader


###############################################################################


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


def natural_sort(list_, pos, subtoken=None):

    """Reorder a list by natural order.

    Reorders a list L by natural order. Sorting occurs by the token at
    index = position. If subtoken is supplied, sorting occurs on the
    alphanumeric subtoken at that index, otherwise sorting is on the
    left-most alphanumeric subtoken.

    Arguments:
        list_ (list): The list to be sorted.

        pos (int): The index position for the item in the list on
                   which we base the sort.

        subtoken (int): The subtoken index position. Optional. Default
                        value is None.

    Returns:
        The sorted list.

    """

    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def split(key, pos):
        stripped = string_tools.strip_non_alphanumeric(key[pos])
        return filter(None, re.split("([0-9]+)", stripped))

    def alphanum_key(key):

        try:
            subtoken_list = [convert(c) for c in split(key, pos)]
        except IndexError as e:
            logger.error("IndexError: {0}".format(e))
            return 0

        try:
            temp_list = [i for i in xrange(subtoken, len(subtoken_list))]
            return [subtoken_list[s] for s in temp_list]
        except (IndexError, TypeError) as e:
            logger.error("IndexError, TypeError: {0}".format(e))
            return subtoken_list

    return sorted(list_, key=alphanum_key)


def sort_subsort(list_, sort_map, header=False, delimiter=","):

    """Return a sorted list.

    Arguments:
        list_ (list): Either a list of strings with delimited tokens or a list
                      of lists of tokens. (Cannot be a mixture of both.)

        sort_map (list): A list of integers or a list of tuples. If given as a
                         list of integers these are assumed to be token indices
                         with no subtoken index, and a subtoken index of zero
                         is added.

                  If sort_map is a list of tuples each must consist of two
                  integers, where the first integer of each tuple is a
                  primary sort index (mapping to a token), and the second
                  integer is a subtoken sort index (mapping to an
                  alphanumeric subtoken of the token).

        header (bol): True if there is a header line, False otherwise.
                      Optional. Default value is False.

        delimiter (str): A delimiter for the strings in list_. Optional.
                         Default value is a comma (",").

    Returns:
        A list of strings with delimited tokens, sorted.

    Notes:

        sort_map = [(A, a), (B, b), (C, c) ...]

        For each tuple:
            The first element is an integer specifying the target token
            index number for the primary, secondary, tertiary, etc. sorts.

            The second element is an integer specifying the alphanumeric
            subtoken index for the given sort.

        Sort strategy:

        (Referring to sort_map above.)

        (1) First sort list_ by the token at index A, starting at subtoken a.

        (2) For all lines in list_ that match on the token at index A, sort by
            the token at index B, starting at subtoken b.

        (3) For all lines in list_ that match on the token at index B, sort by
            the token at index C, starting at subtoken c.

        .... and so on.

    Example:

        sort_map = [(4,0), (4,1), (1,3)]

        This means we will sort first on the tokens in column 4, using the
        subtokens at index zero, then the subtokens at index one, and then on
        the tokens in column 1, using subtokens at index three.

        (0th)       (1st)       (2nd)        (3rd)          (4th)
        Sample_ID	Sample_Name	Sample_Plate Sample_Well	Sample_Project
        2-536381	BTY659A2081	27-116458	 1:01	        LIU583
        2-536382	BTY659A2082	27-116458	 1:01	        LIU583
        2-536383	BTY659A2083	27-116459	 1:01	        LIU582
        2-536384    BTY659A2084 27-116459    1:01           LIU582
        2-536385    BTY659A2085 27-116460    1:01           BTY217
        2-536386    BTY659A2086 27-116460    1:01           BTY217
        2-536387    BTY659A2087 27-116461    1:01           BTY218
        2-536388    BTY659A2088 27-116461    1:01           BTY218

        The first sort is on the tokens in column index 4 (Sample_Project),
        subtoken index 0. The second sort is on tokens in the same column, at
        subtoken index 1.

        Split each token by alphabetic and numeric subtokens:

                       (0th)  (1st)
            LIU583 --> "LIU", "583"
            LIU583 --> "LIU", "583"
            LIU582 --> "LIU", "582"
            LIU582 --> "LIU", "582"
            BTY217 --> "BTY", "217"
            BTY217 --> "BTY", "217"
            BTY218 --> "BTY", "218"
            BTY218 --> "BTY", "218"

        First sort is on the subtokens at index 0:

        Sample_ID	Sample_Name	Sample_Plate Sample_Well	Sample_Project
        2-536385    BTY659A2085 27-116460    1:01           BTY217
        2-536386    BTY659A2086 27-116460    1:01           BTY217
        2-536387    BTY659A2087 27-116461    1:01           BTY218
        2-536388    BTY659A2088 27-116461    1:01           BTY218
        2-536381	BTY659A2081	27-116458	 1:01	        LIU583
        2-536382	BTY659A2082	27-116458	 1:01	        LIU583
        2-536383	BTY659A2083	27-116459	 1:01	        LIU582
        2-536384    BTY659A2084 27-116459    1:01           LIU582

        Second sort is on the subtokens at index 1:

        Sample_ID	Sample_Name	Sample_Plate Sample_Well	Sample_Project
        2-536385    BTY659A2085 27-116460    1:01           BTY217
        2-536386    BTY659A2086 27-116460    1:01           BTY217
        2-536387    BTY659A2087 27-116461    1:01           BTY218
        2-536388    BTY659A2088 27-116461    1:01           BTY218
        2-536383	BTY659A2083	27-116459	 1:01	        LIU582
        2-536384    BTY659A2084 27-116459    1:01           LIU582
        2-536381	BTY659A2081	27-116458	 1:01	        LIU583
        2-536382	BTY659A2082	27-116458	 1:01	        LIU583

        The third sort in on the tokens at column 1 (Sample_Name),
        at subtoken 3.

        Split each token by alphabetic and numeric subtokens:

                            0th    1st    2nd   3rd
            BTY659A2085 --> "BTY", "659", "A", "2085"
            BTY659A2086 --> "BTY", "659", "A", "2086"
            ... and so on.

        Within groups with matching values from the second sort, sort by the
        index-3 subtokens. (This does not change the order of the lines for
        this example.)

    """

    if not list_:
        logger.warning("list_ is empty. Returning.")
        return list_

    final_sort = []

    # If there is a header line, pop it from the unsorted list_ and add it to
    # the final, sorted list.

    if header:
        final_sort.append(list_.pop(0))

    # First branch: strings with delimited tokens.
    # Second branch: list of lists of tokens.
    # Third branch: error.

    if check_types(list_, basestring):
        current_sort = [line.split(delimiter) for line in list_]
    elif check_types(list_, list):
        current_sort = list_
    else:
        logger.error("All members of list_ must be of type str or list.")
        return list_

    # Add zero subtoken index if not provided, or check that all tuples are
    # of length two.

    if check_types(sort_map, int):
        sort_map = [(t, 0) for t in sort_map]
    elif check_types(sort_map, tuple):
        if not all(len(t) == 2 for t in sort_map):
            logger.error("All tuples in sort_map must be of length 2.")
            return list_
    elif not check_types(sort_map, tuple):
        logger.error("All members of sort_map must be of type int or tuple.")
        return list_

    first_run = True

    for t in sort_map:

        sub_lists = LastUpdatedOrderedDict()

        p = t[0]  # primary token
        s = t[1]  # subtoken

        if first_run:
            current_sort = natural_sort(current_sort, p, s)
            pre_p = p  # use first primary token for the second run
            first_run = not first_run

        else:
            for line in current_sort:

                try:
                    sub_lists[line[pre_p]].append(line)
                except KeyError:
                    sub_lists[line[pre_p]] = []
                    sub_lists[line[pre_p]].append(line)
                except IndexError as e:
                    logger.error("IndexError: {0}".format(e))
                    return list_

            pre_p = p  # set previous primary token for the next loop
            current_sort = []

            for key, sub_list in sub_lists.iteritems():

                sub_list_sort = natural_sort(sub_list, p, s)

                for line in sub_list_sort:
                    current_sort.append(line)

    for line in current_sort:
        final_sort.append(",".join(line))

    return final_sort


def quicksort(list_):

    """The standard quick sort algorithm, applied to members of list L.

    Arguments:

        list_(list): A list of items to be sorted.

    """

    if not isinstance(list_, list):
        logger.error("Argument must be of type list.")
        return list_

    less = []
    equal = []
    greater = []

    if len(list_) > 1:
        pivot = list_[0]
        for x in list_:
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            elif x > pivot:
                greater.append(x)

        # Recursive calls
        return quicksort(less) + equal + quicksort(greater)

    else:
        return list_

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
