"""
Provides base classes.

Provided Classes
------------------

ConfigReader
    A class to read configuration files.

Singleton
    A metaclass to provide singletons.

UniqueInstancesClass
    A metaclass to provide instances with unique identification attributes.

"""

import logging
import os
from ConfigParser import ConfigParser
from ConfigParser import InterpolationMissingOptionError
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
from ConfigParser import RawConfigParser
from logging.handlers import RotatingFileHandler

import __main__


##############################################################################


class Singleton(type):

    """A standard singleton metaclass.

    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = cls.__name__
        if name not in cls._instances.keys():
            logger.info("Creating new {0} instance.".format(name))
            cls._instances[name] = super(Singleton, cls).__call__(*args)
        else:
            logger.info("A {0} instance already exists.".format(name))
        return cls._instances[name]


###############################################################################


class UniqueInstancesClass(type):

    """A metaclass to provide instances with a unique identifier.

    """

    _instances = {}
    _id = None

    def __call__(cls, *args, **kwargs):

        """Implements a factory pattern to return a new instance if there is no
        existing instance with the same _id.

        Args:
            *args: positional arguments.

            **kwargs: keyword arguments.

        Returns:
            A new instance if there is no existing instance with the same id_,
            otherwise returns the existing instance with that id_.

        Notes:
            Skips __init__ methods in all derived classes if returning an
            existing instance.

            It is assumed that either the SECOND or FIRST positional argument
            or the FIRST keyword argument provides a unique identifier for a
            particular child type (cls.__name__). The child type (cls.__name__)
            is combined with this identifier to create an identifier that is
            unique across all child types that inherit from this class.

            Order preference for the unique identifier:

                1st: SECOND position argument.
                2nd: FIRST position argument.
                3rd: FIRST keyword argument.

        """

        if args:
            if len(args) >= 2:
                unique_identifier = args[1]
            else:
                unique_identifier = args[0]
        elif kwargs:
            unique_identifier = kwargs[kwargs.keys()[0]]
        else:
            message = ("Attempted to create instance of {0} without "
                       "any parameters. Returning None"
                       .format(cls.__name__))
            logger.warning(message)
            return None

        cls._id = "{0}:{1}".format(cls.__name__, unique_identifier)

        if cls._id not in cls._instances:
            logger.info("Creating new instance of {0} with id_ {1}"
                        .format(cls.__name__, cls._id))
            self = cls.__new__(cls, *args)
            cls._instances[cls._id] = self
            cls.__init__(self, *args, **kwargs)
        else:
            logger.info("An instance of {0} with id_ {1} already exists.".
                        format(cls.__name__, cls._id))

        return cls._instances[cls._id]

    def __init__(cls, *args, **kwargs):

        """Initialize the child class instance.

        Args:
            *args:  positional arguments.

            **kwargs: keyword arguments.

        """

        super(UniqueInstancesClass, cls).__init__(cls)

    @classmethod
    def get_instances(cls):
        return cls._instances


###############################################################################


class ConfigReader(object):

    """Manages configuration files.

    Attributes:
         config (obj): A ConfigParser object.

         config_file (str): A configuration filepath

    """

    __metaclass__ = UniqueInstancesClass

    def __new__(cls, config_file):

        return super(ConfigReader, cls).__new__(cls)

    def __init__(self, config_file):

        """Initializes a OrderFormsConfigMgr object.

        Arguments:
             config_file (str): Full pathname of the configuration file.

        """

        self.config = ConfigParser()
        self.config_file = config_file
        self.raw_config = RawConfigParser()

        try:
            self.config.readfp(open(self.config_file))
        except IOError as e:
            print e
            logger.error("IOError: {0}".format(e))
            raise

    def get_item(self, section, item):

        """Return an item from the configuration file.

        Arguments:
            section (str): Configuration section.

            item (str): Configuration item.

        """

        try:
            return self.config.get(section.lower(), item.lower())
        except (NoOptionError, NoSectionError), e:
            print e
            logger.error("NoOptionError, NoSectionError: {0}".format(e))
            raise
        except InterpolationMissingOptionError, e:

            try:
                self.raw_config.readfp(open(self.config_file))
            except IOError as e:
                logger.error("IOError: {0}".format(e))
                raise

            return self.raw_config.get(section.lower(), item.lower())

    def get_item_as_list(self, section, item):

        """Return an item as a tokenized list of items.

        Arguments:
            section (str): Configuration section.

            item(str): Configuration item.

        Notes: Delimiter is a comma.

        """

        return self.get_item(section, item).split(",")

    def _get_section_pairs(self, section):

        """Return section pairs (variable, value) from the configuration file.

        Arguments:
            section (str): Configuration section.

        """

        try:
            return self.config.items(section.lower())
        except NoSectionError as e:
            print e
            logger.error("NoSectionError: {0}".format(e))
            raise

    def get_section_pairs(self, section, target=None):

        """Return list pairs (variable, value) from the configuration file,
           where the variable name contains the target as a substring.

        Arguments:
            section (str): Configuration section.

            target (str): Substring to match to variable name. Optional.
                          Default value is None.

        """

        if target is None:
            return self._get_section_pairs(section)
        else:
            return [sp for sp in self._get_section_pairs(section)
                    if target in sp[0]]

    def get_section_items(self, section, target=None):

        """Return list of values from the configuration file, where the
           variable name contains target as a substring.

        Arguments:
            section (str): Configuration section.

            target (str): Substring to match to variable name. Optional.
                          Default value is None.

        """

        return [sp[1] for sp in self.get_section_pairs(section,
                                                       target)]

    def get_section_items_as_lists(self, section, target=None):

        """Return list of values from the configuration file, where the
           variable name contains target as a substring.

           Within the list, items are returned as tokenized lists.

        Arguments:
            section (str): Configuration section.

            target (str): Substring to match to variable name. Optional.
                          Default value is None.

        """

        return [sp[1].split(",")
                for sp in self.get_section_pairs(section, target)]

    def get_section_items_as_map(self, section, target=None):

        """Return a map of the section items, where it's expected that each
        item consists of a comma-delimited pair. The first member is the key
        and the second member is the data value. If an item consists of only
        one member, it's assumed the key and data value are identical.

        Args:
            section (str): Section name.

            target (str): Substring to match to variable name. Optional.
            Default value is None.

        Returns: A map.

        """

        return_map = {}

        for sp in self.get_section_items_as_lists(section, target):
            if len(sp) == 2:
                return_map[sp[0].strip()] = sp[1].strip()
            else:
                return_map[sp[0].strip()] = sp[0].strip()

        return return_map

    def update_item(self, section, item, value):

        """Updates an existing item in the configuration file.

        Arguments:
            section (str): Configuration section.

            item (str): Configuration item.

            value (str): The new value for item.

        """

        try:
            self.config.set(section, item, value)
        except (NoSectionError, NoOptionError) as e:
            print e
            logger.error("NoSectionError, NoOptionError: {0}".format(e))
            return None

        with open(self.config_file, "w") as f:
            self.config.write(f)


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
