"""
A library of functions to build HTML code.

Provided functions
------------------
create_paragraph
    Return a formatted HTML paragraph.

create_table
    Return a formatted HTML table.

"""

import logging
import os
from logging.handlers import RotatingFileHandler

import __main__

from library_tools import ConfigReader


###############################################################################


def create_paragraph(text):

    """Return a string containing a formatted HTML paragraph.

    """

    try:
        return "<p>{0}</p>".format(text.replace("\n", "<br />"))
    except AttributeError as e:
        logger.error("AttributeError: {0}".format(e))
        return text


def create_table(table):

    """Return a string containing a formatted HTML table.

    Arguments:
        table (dict): A dictionary containing the data to be parsed into an
                      HTML table.

                      table should be structured as follows:

                      table = {key_1 : ["a1", "b1", "c1", ...],
                               key_2 : ["a2", "b2', "c2", ...],
                               .
                               .
                               .}

                      If any key == "header" or "headers", we assume the
                      associated list contains column headings.

    """

    if not isinstance(table, dict):
        logger.error("Argument must be of type dict.")
        return "No table was created."

    html_table = ("<table border=\"1\" { "
                  ".tg  {border-collapse:collapse;border-spacing:0;"
                  "margin:0px auto;}"
                  ".tg td{font-family:Arial, sans-serif;font-size:14px;"
                  "padding:10px 5px;border-style:solid;border-width:1px;"
                  "overflow:hidden;word-break:normal;}"
                  ".tg th{font-family:Arial, sans-serif;font-size:14px;"
                  "font-weight:normal;padding:10px 5px;border-style:solid;"
                  "border-width:1px;overflow:hidden;word-break:normal;}"
                  ".tg .tg-h6r7{font-weight:bold;font-size:12px;"
                  "font-family:Arial, Helvetica, sans-serif !important;;"
                  "vertical-align:top}"
                  ".tg .tg-yw4l{vertical-align:top} } class=\"tg\">")

    for key, _list in table.iteritems():

        html_table += "<tr>"

        for item in _list:

            if str(key).lower() in ("header", "headers"):
                html_table += "<th class=\"tg-h6r7\">{0}</th>".format(item)
            else:
                html_table += "<td class=\"tg-yw4l\">{0}</td>".format(item)

        html_table += "</tr>"

    html_table += "</table>"

    return html_table

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
