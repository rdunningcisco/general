"""
Provides functions and classes to manipulate dictionaries.

Provided Functions
------------------

find_common_value_keys
    Returns a list of keys that all map to the same value.

find_dictionary_with_max_key
    Returns a dictionary whose key value is the maximum from a list of
    dictionaries.

insert
    Inserts source dictionary into target dictionary. Returns new target
    dictionary.

invert_map
    Inverts key-value pairs. Returns new, inverted dictionary.

key_sets
    Returns a list of unique keys from a list of dictionaries.

list_pairs
    Lists key-values pairs.

merge
    Merges source dictionary into target dictionary to create a new dictionary.

replace_entry
    Replaces a key, value pair in a dictionary.

Provided Classes
----------------

LastUpdatedOrderedDict
     Extends the OrderedDict class to create a dictionary that remembers the
     order in which key-value pairs are added.

OrderedSet
    Stores set items in the order in which they were added.

"""

import logging
import os
from collections import MutableSet
from collections import OrderedDict
from logging.handlers import RotatingFileHandler

import __main__

from library_tools import ConfigReader


###############################################################################


def find_common_value_keys(dictionary, value):

    """Return a list.

    Find all the keys in the given dictionary that map to a common value.

    Args:
        dictionary (dict): A dictionary.

        value (varies): A specific value.

    """

    try:
        return [k for k in dictionary.keys() if value in dictionary[k]]
    except TypeError:
        return [k for k in dictionary.keys() if value == dictionary[k]]


def find_dictionary_with_max_key(d_list, key):

    """Return a dictionary.

    Finds the dictionary in d_list whose key value is a maximum for the list.

    Args:
        d_list (list): A list of dictionaries.

        key (str): The target key.

    Returns:
        A dictionary.

    """

    return max(d_list, key=lambda x: x[key])


def insert(source, target):

    """Inserts source dictionary s into target dictionary t.

    Arguments:
        source (dict): Source dictionary.

        target (dict): Target dictionary.

    """

    try:
        target.update(source)
    except (AttributeError, ValueError, TypeError) as e:
        print "Exception: {0}".format(e)
        logger.error("AttributeError, ValueError, TypeError: {0}".format(e))

    return target


def invert_map(map_):

    """Return an inverted map.

    Arguments:
        map_ (dict): A dictionary.

       (Much simpler to do in Python 2.7 or 3+.)

    """

    im = {}

    try:
        for k, v in map_.iteritems():
            try:
                for i in v:
                    try:
                        im[i].append(k)
                    except KeyError:
                        im[i] = []
                        im[i].append(k)
            except TypeError:
                im[v] = k

        return im

    except AttributeError as e:
        print "Exception: {0}".format(e)
        logger.error("AttributeError: {0}".format(e))
        return map_


def key_set(dictionaries):

    """Return a list of keys from a list of dictionaries, with each key
    appearing only once in the list.

    Arguments:
        dictionaries (list): A list of dictionaries.

    Returns:
        A list of keys.

    Example:
        dict_1 = {"a":1, "b":2, "c":3}
        dict_2 = {"a":4, "d":5, "e":6}
        dict_3 = {"b":7, "c":8, "f":9}

        return ["a", "b", "c", "d", "e", "f"]

    """

    try:
        return list(OrderedSet([k for d in dictionaries for k in d.keys()]))
    except (AttributeError, IndexError) as e:
        print "Exception: {0}".format(e)
        logger.error("AttributeError, IndexError: {0}".format(e))
        return None


def list_pairs(d):
    """Write to stdout the key-value pairs of the given dictionary.

    Args:
        d (dict): A dictionary object.

    Returns:
        None.

    """

    for k, v in d.iteritems():
        print "k: {0}; v: {1}".format(k, v)


def merge(source, target):

    """Merge source dictionary s into target dictionary t as a new
       dictionary (shallow copy).

       Arguments:
           source (dict): source dictionary.

           target (dict): target dictionary.

       Returns:
           A merged dictionary. The original dictionaries s, t are not
           modified by this function.

       Notes:
           If a key exists in both dictionaries, the value in s
           overwrites the value in t.

   """

    try:
        return insert(source, target.copy())
    except (AttributeError, ValueError, TypeError) as e:
        print "Exception: {0}".format(e)
        logger.error("AttributeError, ValueError, TypeError: {0}".format(e))
        return target


def replace_entry(d, k_old, k_new, v_new):

    """Replace a key-value pair in a dictionary.

    Args:
        d (dict): The target dictionary.

        k_old: Key to be replaced.

        k_new: Kew to be added.

        v_new: Value to be added.

    Returns:
        The updated dictionary.

    """

    del d[k_old]

    d[k_new] = v_new

    return d

################################################################################


class LastUpdatedOrderedDict(OrderedDict):

    """Stores dictionary elements in the same order in which they were added.

    """

    def __setitem__(self, key, value):

        """Map the input value to the input key.

        Arguments:
            key (str): The key that maps to value.

            value (str): The value that is mapped by key.

        """

        if key in self:
            del self[key]

        OrderedDict.__setitem__(self, key, value)

    def next_key(self, key):

        """Return the next key in the dictionary, unless it's the last key.

        Args:
            key (str): The dictionary key value.

        Returns:
            The next item in the dictionary (associated with the key).

        """

        next_item = self._OrderedDict__map[key][1]
        if next_item is self._OrderedDict__root:
            print "ERROR: {0} is the last key!".format(key)
        return next_item[2]

    def first_key(self):

        """Return the first key in the dictionary.

        """

        for key in self:
            return key

        print "ERROR: OrderedDict() is empty"


###############################################################################


class OrderedSet(MutableSet):

    """Stores set items in the order in which they were added.

    Source: http://code.activestate.com/recipes/576694/

    """

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

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



