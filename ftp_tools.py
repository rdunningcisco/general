"""
Provides classes for FTP steps.

Provided Classes
----------------

FTPConnection
    Provides basic FTP tools.

FTPToolsError
    Custom exception class.

"""

import logging
import os
import socket
import string
from logging.handlers import RotatingFileHandler

import __main__
import paramiko

from exceptions_library import CustomExceptionBasic
from library_tools import ConfigReader


###############################################################################


class FTPConnection(object):

    """Provides functions for FTP operations.

    Attributes:
        servername (str): Name of the FTP server.

        port (str): Port number for the FTP server.

        username (str): Username for FTP access.

        password (str): Password for FTP access.

        transport (obj): A paramiko Transport object.

        sftp_client (obj): A paramiko SFTPClient object.

        ssh_client (obj): A paramiko SSHClient object.

        scp_client (obj): An scp SCPClient object.


    """

    def __init__(self, servername, port, username, password):

        """Initialize an FTPConnection object.

        Arguments:
            servername (str): Client servername.

            port (int): Port number.

            username (str): Username.

            password (str): Password.

        """

        logger.info("Initializing for servername: {0}".format(servername))

        self.servername = servername
        self.port = port
        self.username = username
        self.password = password
        self.transport = None
        self.sftp_client = None
        self.ssh_client = None
        self.scp_client = None

    def set_transport(self):

        """Sets the transport object.

        """

        logger.debug("self.servername: {0}".format(self.servername))
        logger.debug("self.port: {0}".format(self.port))
        logger.debug("self.username: {0}".format(self.username))
        logger.debug("self.password: {0}".format(self.password))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.transport = paramiko.Transport((self.servername, self.port))

        self.transport.connect(username=self.username, password=self.password)

    def set_sftp_client(self):

        """Sets the sftp_client object.

        """

        if self.transport is None:
            self.set_transport()

        self.sftp_client = paramiko.SFTPClient.from_transport(self.transport)

    def set_ssh_client(self):

        """Sets the ssh_client object.

        """

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.servername, self.port, self.username,
                                self.password)

    def set_scp_client(self):

        """Sets the scp_client object.

        """

        if self.ssh_client is None:
            self.set_ssh_client()

        # self.scp_client = SCPClient(self.ssh_client.get_transport())

    def sftp_put(self, filename, location):

        """Puts a file in a specified filepath using sftp.

        Arguments:
            filename (str): Filename.

            location (str): File filepath.

        """

        tokens = location.split("/")

        for i in xrange(1, len(tokens)):

            temp_path = "/" + string.join(tokens[1:i], "/")

            try:
                self.sftp_client.chdir(temp_path)
            except Exception as e:
                logger.error("chdir Exception: {0}".format(e))
                try:
                    self.sftp_client.mkdir(temp_path)
                except Exception as e:
                    logger.error("mkdir Exception: {0}".format(e))
                    raise ValueError

        try:
            self.sftp_client.put(filename, location)
        except Exception as e:
            logger.error("Put Exception: {0}".format(e))

        self.close_connections()

    def sftp_rename(self, old_path, new_path):

        """Renames old_path to new_path

        Args:
            old_path (str): old path name, to be replaced

            new_path (str): new path name.

        Returns: None.

        """

        try:
            self.sftp_client.rename(old_path, new_path)
        except Exception as e:
            logger.error("rename Exception: {0}".format(e))

    def scp_put(self, filename, original_location, new_location):

        """Puts a file in a specified filepath using scp.

        Arguments:
            filename (str): Filename.

            original_location (str): The original file filepath.

            new_location (str): The new file filepath.

        """

        arguments = ("arguments:"
                     "\n\tfilename: {0}"
                     "\n\toriginal_location: {1}"
                     "\n\tnew_location: {2}".format(filename,
                                                    original_location,
                                                    new_location))

        logger.info("{0}".format(arguments))

        cd = "cd {0}".format(new_location)

        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(cd)

        results = ("\n\tssh_stdin: {0}"
                   "\n\tssh_stdout: {1}"
                   "\n\tssh_stderr: {2}".format(ssh_stdin, ssh_stdout,
                                                ssh_stderr))

        logger.debug("{0}".format(results))

        self.scp_client.put(original_location + filename,
                            new_location + filename)

        self.close_connections()

    def close_connections(self):

        """Close open connections.

        """

        connections = [self.transport, self.sftp_client, self.ssh_client,
                       self.scp_client]

        connections = filter(None, connections)

        for i in connections:
            i.close()

###############################################################################


class FTPToolsError(CustomExceptionBasic):

    """Custom Exception class.

    Attributes:

        message (str): Error message.

    """

    def __init__(self, message=None):

        """Initialize the object.

        Args:
            message (str): Error message.

        """

        self.message = "ftp_tools error" if message is None else message

        super(FTPToolsError, self).__init__(message)


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
