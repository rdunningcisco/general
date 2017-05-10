"""
Provides general tools for GUI applications using Tkinter.

Provided Functions
------------------

confirm_item
    Raises a warning box if item is None or empty.

error
    Raises an error box.

message
    Raises a message box.

Provided Classes
------------------

PopUpWindow
    Base class for pop-up windows. Provides an "Ok" button and a "Cancel"
    button.

DualScrolledFrame
    Extends the Tkinter.Frame object to include horizontal and vertical scroll
    bars.

ExcelLikeTable
    Provides an Excel-like table to display data as it would appear in a CSV
    file loaded into Excel.

ReadOnlyTextWidget
    Extends the Tkinter Text object to allow for a read-only state that can
    still be changed by the program.

"""

import Tkinter
import logging
import os
import tkMessageBox
from Tkinter import Button
from Tkinter import Checkbutton
from Tkinter import Entry
from Tkinter import IntVar
from Tkinter import Label
from Tkinter import Message
from Tkinter import StringVar
from Tkinter import Text
from idlelib.WidgetRedirector import WidgetRedirector
from logging.handlers import RotatingFileHandler

import __main__

from library_tools import ConfigReader
from library_tools import UniqueInstancesClass


###############################################################################


def confirm_item(item, title=None, message=None):

    """Raises a warning box if item is None.

    Args:
        item: Generic.

        title (str): Warning box title.

        message (str): A warning message. Optional. Default value is None.

    Returns: Boolean False if item is None or empty; True otherwise.

    """

    title = "Error" if title is None else title
    message = "Item is None or empty." if message is None else message

    if not item:
        error(title=title, message=message)
        return False
    else:
        return True


def error(title=None, message=None):

    """Raises an error box.

    Args:
        title (str): The error box title. Optional. Default value is None.

        message (str): The error message. Optional. Default value is None.

    Returns:

    """

    title = "Error" if title is None else title
    message = "An error has occurred." if message is None else message

    tkMessageBox.showerror(title=title, message=message)


def message(title=None, message=None):

    """Raises a message box.

    Args:
        title (str): The message box title. Optional. Default value is None.

        message (str): The message. Optional. Default value is None.

    Returns: None.

    """

    title = "Information" if title is None else title
    message = "An important message is missing." if message is None else message

    tkMessageBox.showinfo(title=title, message=message)


def warning(title=None, message=None):

    """Raise a warning (attention) box.

    Args:
        title (str): The warning box title. Optional. Default value is None.

        message (str): The warning message. Optional. Default value is None.

    Returns: None.

    """

    title = "Warning" if title is None else title
    message = "You have been warned." if message is None else message

    tkMessageBox.showwarning(title=title, message=message)


###############################################################################

class PopUpWindow(object):

    """Base class for pop up windows. Provides Ok and Cancel buttons. Additional
    elements are defined in the subclass.

    Attributes:

        parent (obj): A Tkinter.Tk() object.

        window (obj): A Tkinter.Toplevel object. Spawns the new pop-up window.

        title (str): The window title.

        initial_focus (obj): Frame or window initially in focus (active).

        bottom_row (int): index number of the bottom-most row where the "Ok" and
                          "Cancell" buttons will be placed. Optional. Default
                          value is 1.

        ok_button (obj): A Tkinter.Button object.

        cancel_button (obj): A Tkinter.Button object.

    """

    __metaclass__ = UniqueInstancesClass

    def __new__(cls, *args, **kwargs):

        """Return a instance of this class.

        Args:
            *args: positional arguments.

            **kwargs: keyword arguments.

        Returns:
            A new (unique) instance of PopUpWindow.

        """

        return super(PopUpWindow, cls).__new__(cls)

    def __init__(self, parent, title="pop up window", message_panel=None,
                 bottom_row=1):

        """Initialize the object.

        Args:
            parent (obj): A Tkinter.Tk() object.

            title (str): The window title.

            bottom_row (int): The index number of the bottom-most grid row
                              where the Ok and Cancel buttons will be placed.
                              Optional. Default value is 1.

        """

        logger.info("Initializing.")

        self.parent = parent
        self.window = Tkinter.Toplevel(self.parent)
        self.frame = Tkinter.Frame(self.window)
        self.frame.grid()
        self.window.title(title)
        self.message_panel = message_panel
        self.window.grab_set()  # makes only this window active
        self.initial_focus = self.window
        self.initial_focus.focus_set()
        self.bottom_row = bottom_row

        # Some general default values:

        self.button_width = 4
        self.button_height = 2
        self.x_padding = 10
        self.y_padding = 10

        # Create the Message Panel, if message text was passed in.

        if self.message_panel is not None:
            self.message = Message(self.frame, text=self.message_panel)
            self.message.grid(row=0, column=0, columnspan=2,
                              padx=self.x_padding, pady=self.y_padding,
                              sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)

            self.message.bind("<Configure>",
                              lambda e: self.message.configure(
                                               width=self.window.winfo_width()))

        # Create the Ok and Cancel buttons.

        self.ok_button = Button(self.frame, text="OK", width=10,
                                command=self.ok,
                                default=Tkinter.ACTIVE)
        self.ok_button.grid(row=self.bottom_row, column=0,
                            padx=self.x_padding, pady=self.y_padding,
                            sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)

        self.cancel_button = Button(self.frame, text="Cancel", width=10,
                                    command=self.cancel)
        self.cancel_button.grid(row=bottom_row, column=1,
                                padx=self.x_padding, pady=self.y_padding,
                                sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)

        self.window.bind("<Return>", self.ok)
        self.window.bind("<Escape>", self.cancel)

        Tkinter.Grid.columnconfigure(self.window, 0, weight=1)
        Tkinter.Grid.columnconfigure(self.window, 1, weight=1)

        for i in xrange(self.bottom_row):
            Tkinter.Grid.rowconfigure(self.window, i, weight=1)

    def cancel(self):

        """Destroy the pop-up and return focus to the parent object.

        Returns: None.

        """

        self.parent.focus_set()
        self.window.destroy()

    def ok(self):

        """Calls the subclass' apply() method, then the cancel() method.

        Returns: None.

        """

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.window.withdraw()
        self.window.update_idletasks()

        self.apply()  # The subclass must provide this method.
        self.cancel()

    def validate(self):

        """Performs a validation check. Overridden in the subclass.

        Returns: None.

        """

        return True  # override in the subclass

################################################################################


class DualScrolledFrame(Tkinter.Frame):

    """Extends the Tkinter.Frame object to include horizontal and vertical
       scrollbars.

        Attributes:
            parent (obj): A Tkinter.Tk() object.

            interior (obj): A Tkinter.Frame object.

        Notes:
            When adding objects to the interior frame, you *must* use the
            interior attribute.

    """

    def __init__(self, parent, *args, **kwargs):

        """Initialize the object.

        Args:
            parent (obj): A Tkinter.Tk() object.

            *args: positional arguments.

            **kwargs: keyword arguments.

        """

        logger.info("Initializing.")

        Tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        # create a canvas object and a horizontal scrollbar for scrolling it
        hscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.HORIZONTAL)
        hscrollbar.pack(fill=Tkinter.X, side=Tkinter.BOTTOM,
                        expand=Tkinter.FALSE)
        vscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.VERTICAL)
        vscrollbar.pack(fill=Tkinter.Y, side=Tkinter.RIGHT,
                        expand=Tkinter.FALSE)

        canvas = Tkinter.Canvas(self, bd=0, highlightthickness=0,
                                xscrollcommand=hscrollbar.set,
                                yscrollcommand=vscrollbar.set)

        canvas.pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH, expand=Tkinter.TRUE)
        hscrollbar.config(command=canvas.xview)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Tkinter.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=Tkinter.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar

        def _configure_interior():
            # update the scrollbars to match the size of the inner frame

            # Change this so that size matches the fully possible size of
            # the displayed data.

            size = (self.interior.winfo_reqwidth(),
                    self.interior.winfo_reqheight())

            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas():

            if self.interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


################################################################################


# noinspection PyShadowingNames,PyShadowingNames
class EnterValuesPopUp(PopUpWindow):

    """Provides a pop up window with which the user enters values.

    Attributes:

    """

    instances = {}

    def __init__(self, parent, title="Enter Values",
                 message=None, variables=None):

        """ Initialize the object.

        Args:
            parent (obj): A Tkinter Tk() object.

            title (str): The title of the pop up window. Optional. Default
                         value is "Enter Values."

            message (str): Message text. Optional. Default value is None.

            variables (list): Entry field prompts. One entry field per variable.

        """

        logger.info("Initializing.")

        message_text = ("Use the fields below to enter appropriate values. "
                        "The values will be recorded when you click Ok.")

        message = message_text if message is None else message

        super(EnterValuesPopUp, self).__init__(parent=parent,
                                               title=title,
                                               message_panel=message,
                                               bottom_row=len(variables)+1)

        self.results = {}
        self.user_entries = {}
        self.variables = variables

        row_index = 1

        for v in self.variables:
            prompt = Label(self.frame, text=v)
            prompt.grid(row=row_index, column=0, padx=self.x_padding,
                        pady=self.y_padding,
                        sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)
            self.user_entries[v] = StringVar()
            entry = Entry(self.frame, textvariable=self.user_entries[v])
            entry.delete(0, Tkinter.END)
            entry.insert(0, "nslm/A")
            entry.grid(row=row_index, column=1,
                       sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)
            row_index += 1

        self.window.wait_window(self.window)

    def apply(self):

        """Apply the user's choices (set self.results).

        Returns: None.

        """

        # self.results = {k: v.get() for k, v in self.user_entries.iteritems()}

        for k, v in self.user_entries.iteritems():
            self.results[k] = v.get()


################################################################################


# noinspection PyShadowingNames,PyShadowingNames
class ReadOnlyTextWidget(Text):

    """Extends the Tkinter Text widget to provide a read-only option that can
       be edited by the code.

       Attributes:

       redirector (obj): A WidgetRedirector object.

       insert (fun): Redirects inserts.

       delete (fun): Redirects deletes.

    """

    def __init__(self, *args, **kwargs):

        """Initialize the object.

        Args:
            *args: Postional arguments for the Text widget.

            **kwargs: Keyword arguments for the Text widget.

        """

        logger.info("Initializing.")

        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args,
                                               **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args,
                                               **kw: "break")

###############################################################################


class SelectItemsPopUp(PopUpWindow):

    """Provides a pop-up window with checkboxes.

    """

    instances = {}

    def __init__(self, parent, title="Selection", variables=None):

        """Initialize the object.

        Args:
            parent (obj): The parent frame.

            title (str): The window title. Optional. Default value is
            "Selection."

            variables (list): One button per variable.

        """

        logger.info("Initializing.")

        message_panel = ("Use the checkboxes below to select which sample "
                         "sheets to remove from the application's active "
                         "list. You can reopen using File ... Load on the "
                         "menu bar.")

        super(SelectItemsPopUp, self).__init__(parent=parent,
                                               title=title,
                                               message_panel=message_panel,
                                               bottom_row=len(variables)+1)

        self.variables = variables
        self.results = None
        self.button_reference_states = []

        row_index = 1

        for v in self.variables:
            button_state = IntVar()
            button_reference = v.split("/")[-1]
            c = Checkbutton(self.frame, text=button_reference,
                            variable=button_state)
            c.grid(row=row_index, column=0, columnspan=2,
                   sticky=Tkinter.N+Tkinter.E+Tkinter.W+Tkinter.S)
            row_index += 1
            button_reference_state = (v, button_state)
            self.button_reference_states.append(button_reference_state)

        self.window.wait_window(self.window)

    def apply(self):

        """Apply the user's choices (set self.results).

        Returns: None.

        """

        self.results = [(r, s.get()) for (r, s) in
                        self.button_reference_states]

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
