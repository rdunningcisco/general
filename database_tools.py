"""
Provides tools to access, query, and update a database.

Provided Classes
----------------

_Database_Connection
    Generic tools to acces, query, and update a database. Inherited by the
    other classes.

DatabaseToolsError
    Custom exception class.

PostgreSQLConnection
    Provides tools to access, query, and update a postgreSQL database.

OracleConnection
    Provides tools to access, query, and update an Oracle database.

"""

import logging
import os
from logging.handlers import RotatingFileHandler

import __main__
import cx_Oracle
import psycopg2  # PostgreSQL

from exceptions_library import CustomExceptionBasic
from library_tools import ConfigReader
from library_tools import UniqueInstancesClass


class _DatabaseConnection(object):

    """Provides generic tools to access, query, and update a database.

    Class variables:
        instances (dict): Maps object id_list to Database connection objects.

    Attributes:
        db_host (str): Host name for the database.

        db_name (str): Database name.

        db_pass (str): Database user password.

        db_port (str): Database port number.

        db_servicename (str): Database service name.

        db_user (str): Database username.

        _object (obj): External object to facilitate the connection.

        _error (obj): Primary error object for _object.

        db_conn (obj): Database connection object.

        db_cursor (obj): Database cursor object.

    """

    __metaclass__ = UniqueInstancesClass

    instances = {}

    def __new__(cls, *args, **kwargs):

        """Return a new instance of this class.

        """

        return super(_DatabaseConnection, cls).__new__(cls)

    def __init__(self, db_host, db_name, db_pass, db_port, db_servicename,
                 db_user, _object, _error):

        """Initialize the object.

        Arguments:
            db_host (str): Database host name.

            db_name (str): Database name.

            db_pass (str): Database user password.

            db_port (str): Database port number.

            db_servicename (str/None): Database service name.

            db_user (str): Database username.

            _object (obj): Imported database connection object.

            _error (obj): _object's _error object.

        Notes:
            Notice that the argument names are in alphabetical order.

        """

        self.db_host = db_host
        self.db_name = db_name
        self.db_pass = db_pass
        self.db_port = db_port
        self.db_servicename = db_servicename
        self.db_user = db_user
        self._object = _object
        self._error = _error
        self.db_conn = None
        self.db_cursor = None
        self.conn_string = None

    @staticmethod
    def close_connections():

        """Close all open Database db_conn and db_cursor objects.

        """

        for id_, instance in _DatabaseConnection.instances.iteritems():
            instance.db_cursor.close()
            instance.db_conn.close()
            logger.info("Closed connections for {0}".format(id_))

    def set_db_conn(self):

        """Set a database connection.

        Raises:
            DatabaseToolsError: Raised by _object. Usually indicates a database
                error.

        """

        try:
            self.db_conn = self._object.connect(self.conn_string)
            logger.info("Successful connection. Setting cursor next.")
        except self._error as e:
            logger.error("There was a connection error.")
            logger.error("Error message: {0}".format(e))
            logger.error("self.conn_string: {0}".format(self.conn_string))
            raise DatabaseToolsError(e)

        if self.db_conn is not None:
            self.set_db_cursor()
            _DatabaseConnection.instances[id(self)] = self
        else:
            logger.error("Unable to set cursor. No database connection.")

        for k, v in self.__dict__.iteritems():
            logger.info("k: {0}; v: {1}".format(k, v))

    def set_db_cursor(self):

        """Set a database cursor.

        Raises:
            _error: Raised by _object. Usually indicates a database error.

            AttributeError: self.db_conn does not reference a database
                            connection object.

        """

        try:
            self.db_cursor = self.db_conn.cursor()
            logger.info("The cursor is set.")
        except (self._error, AttributeError) as e:
            logger.error("There was a cursor error.")
            logger.error("Error message: {0}".format(e))
            raise DatabaseToolsError(e)

    def query_db(self, query_string):

        """Query the database. Returns the query results as a list.

        Arguments:
            query_string (str): An SQL query.

        Returns:
            A list of string tokens.

        Raises:
            _error: Raised by _object. Usually indicates a database error.

            AttributeError: self.db_cursor does not reference a database cursor
                            object.

            TypeError: Mal-formed arguments.

        """

        try:
            self.db_cursor.execute(query_string)
        except (self._error, AttributeError, IndexError, TypeError) as e:
            logger.error("An error occurred with the query.")
            logger.error("query_string: {0}".format(query_string))
            logger.error("Error message: {0}".format(e))
            raise DatabaseToolsError(e)

        try:
            results = self.db_cursor.fetchall()
            return results
        except (self._error, AttributeError) as e:
            logger.error("An error occurred with fetchall.")
            logger.error("Error message: {0}".format(e))
            return None

    def commit(self):

        """Commit changes to the database.

        Raises:
            _error: Raised by _object. Usually indicates a database error.

        """

        try:
            self.db_conn.commit()
        except self._error as e:
            logger.error("An error occurred with the commit.")
            logger.error("Error message: {0}".format(e))
            raise DatabaseToolsError(e)

    def close(self):

        """Close the database connection.

        """

        if self.db_conn is not None:
            self.db_conn.close()
            self.db_conn = None

        if self.db_cursor is not None:
            self.db_cursor = None


###############################################################################


class PostgreSQLConnection(_DatabaseConnection):

    """Provides tools to access, query, and update a postgreSQL database.

    Attributes:
        conn_string (str): The connection string.

    """

    def __init__(self, db_host, db_name, db_pass, db_port, db_user):

        """Initialize the object.

        Arguments:
            db_host (str): Database host name.

            db_name (str): Database name.

            db_pass (str): Database user password.

            db_port (str): Database port number.

            db_user (str): Database username.

        """

        super(PostgreSQLConnection, self).__init__(db_host, db_name, db_pass,
                                                   db_port, None, db_user,
                                                   psycopg2, psycopg2.Error)

        self.conn_string = ("host = {0} dbname = {1} password = {2} "
                            "port = {3} user = {4}".format(self.db_host,
                                                           self.db_name,
                                                           self.db_pass,
                                                           self.db_port,
                                                           self.db_user))


###############################################################################


class OracleConnection(_DatabaseConnection):

    """Provides tools to access, query, and update an Oracle database.

    """

    def __init__(self, db_host, db_name, db_pass, db_port, db_servicename,
                 db_user):

        """Initialize the object.

        Arguments:
            db_host (str): Database host name.

            db_name (str): Database name.

            db_pass (str): Database user password.

            db_port (str): Database port number.

            db_servicename (str): Database service name.

            db_user (str): Database username.

        """

        super(OracleConnection, self).__init__(db_host, db_name, db_pass,
                                               db_port, db_servicename, db_user,
                                               cx_Oracle,
                                               (cx_Oracle.DatabaseError,
                                                cx_Oracle.InterfaceError))

        self.conn_string = "{0}/{1}@{2}:{3}/{4}".format(self.db_user,
                                                        self.db_pass,
                                                        self.db_host,
                                                        self.db_port,
                                                        self.db_servicename)

        logger.info("self.conn_string: {0}".format(self.conn_string))

###############################################################################


class DatabaseToolsError(CustomExceptionBasic):

    """Custom Exception class.

    Attributes:

        message (str): Error message.

    """

    def __init__(self, message=None):

        """Initialize the object.

        Args:
            message (str): Error message.

        """

        self.message = "database error" if message is None else message

        super(DatabaseToolsError, self).__init__(message)

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
