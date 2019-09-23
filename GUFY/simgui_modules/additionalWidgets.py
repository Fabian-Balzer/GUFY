# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all functions and classes used for the creation of the other
widgets and some Dialogs not covered by the other modules.

This module is structured as follows:
    - Functions for creating the Status Bar
    - Functions for creating and setting up the Slider for time series
    - The coolSpinBox class and functions for SpinBoxes
    - The PlotAllDialog class for the options of plotting multiple files
    - The RecalcDialog class for recalculating extrema in time series mode
    - The coolAction class and function for creating the MenuBar
"""


import PyQt5.QtWidgets as QW
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
from math import ceil
from simgui_modules.checkBoxes import coolCheckBox
from simgui_modules.helpWindows import HelpWindow
from simgui_modules.logging import StatusHandler, GUILogger


# %% Functions for creating the Status Bar
def createAllStatusInfo(Param_Dict, Bar_Dict):
    """Creates Status bar and corresponding labels and stores them in Bar_Dict.
    params:
        Param_Dict: For file information.
        Bar_Dict: Dictionary where labels and bar are stored.
    """
    LabelList = createStatusLabels(Param_Dict)
    keys = ["Status", "Dir", "File", "Series"]
    for i in range(4):
        Bar_Dict[keys[i]] = LabelList[i]
    Bar_Dict["Bar"] = createStatusBar(Bar_Dict)


def createStatusBar(Bar_Dict):
    """Initializes the status bar for the Window.
    params:
        Bar_Dict: Dictionary for Labels to be added
    returns:
        bar: Status Bar for the Window
    """
    bar = QW.QStatusBar()
    Wid_StatusBar = QW.QWidget()
    Lay_StatusBar = QW.QHBoxLayout(Wid_StatusBar)
    Lay_StatusBar.addWidget(Bar_Dict["Status"])
    horSpacer = QW.QSpacerItem(10000, 1, QW.QSizePolicy.Expanding, QW.QSizePolicy.Minimum)
    Lay_StatusBar.addItem(horSpacer)
    keys = ["Dir", "File", "Series"]
    for key in keys:
        Lay_StatusBar.addWidget(Bar_Dict[key])
    bar.addPermanentWidget(Wid_StatusBar)
    return bar


def createStatusLabels(Param_Dict):
    """Creates the Status Labels for the status bar and stores them in a list.
    returns:
        statusList: List containing [status, directory, file, seriesname]
    """
    status = QW.QLabel("Click 'Open file' to start.")
    StatusHandler.newText.connect(status.setText)
    StatusHandler.newText.connect(status.repaint)
    status.setFixedWidth(500)
    directory = QW.QLabel(Param_Dict["Directory"])
    directory.setMaximumWidth(500)
    file = QW.QLabel(Param_Dict["Filename"])
    seriesname = QW.QLabel(Param_Dict["Seriesname"])
    statusList = [status, directory, file, seriesname]
    return statusList


# %% Functions for creating and setting up the Slider for time series
def createDataSetSlider(Param_Dict, Misc_Dict):
    """Creates a QSlider object to select the file to show for the current
    plot"""
    slider = QW.QSlider(QC.Qt.Horizontal)
    slider.setRange(0, 20)
    slider.setValue(0)
    slider.setTickPosition(QW.QSlider.TicksBelow)
    slider.setTickInterval(1)
    slider.setToolTip("Select the desired data set of the time series.")
    slider.hide()  # It will be shown when the user selects time series mode
    slider.valueChanged.connect(lambda: Param_Dict["SignalHandler"].getSliderInput())
    Misc_Dict["SeriesSlider"] = slider


def setUpWidgets(Param_Dict, CheckBox_Dict, Misc_Dict):
    """Formats the slider and spinner so it fits the time series given."""
    slider = Misc_Dict["SeriesSlider"]
    length = len(Param_Dict["DataSeries"])
    slider.setRange(0, length-1)
    GUILogger.log(29, f"Loaded all {length} datasets of '{str(Param_Dict['Seriesname'])}'.")
    GUILogger.info("They are now ready for plotting.")
    slider.valueChanged.emit(0)
    slider.show()
    spinner = Misc_Dict["ProfileSpinner"]
    spinner.setMaximum(length)
    spinner.setValue(1)
    spinner.setDisabled(False)


# %% The coolSpinBox class and functions for SpinBoxes
class coolSpinBox(QW.QSpinBox):
    """Modified version of QSpinBox
    Creates a QSpinBox with a given range and start value
    params:
        range_: range for the Box
        value: start value. Needs to be in range.
        tooltip: optionally create a tooltip for the edit
    """
    def __init__(self, range_=(0, 100), value=50, tooltip=None, width=250):
        super().__init__()
        self.setRange(*range_)
        self.setValue(value)
        self.setToolTip(tooltip)
        if width:
            self.setFixedWidth(width)
        self.setStyleSheet("""QSpinBox {color: rgb(0,0,0); height: 18px;
                            background: transparent; padding-right: 5px;
                            /* make room for the arrows */}""")

    def textFromValue(self, value):
        """Turn the input value into a fitting string."""
        if value == 1:
            value = ""
        else:
            suf = lambda n: "%d%s "%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
            value = suf(value)
        return value


def createBufferSpinner(width=100):
    """Initialize a Spinner with Range from 100 to 2000.
    returns:
        spinner: QSpinner object for changing buffer size.
    """
    tooltip = "Set buffer size for the plot"
    spinner = coolSpinBox((100, 2000), 800, tooltip, width=width)
    return spinner


def createOnlyEverySpinner(length):
    """Initialize a spinner with dynamic range to later be changed by maximum
    number of DataSets in a TimeSeries."""
    tooltip = "Change the number of datasets that are skipped when making the plots"""
    spinner = coolSpinBox((1, length), 1, tooltip, width=None)
    spinner.setPrefix("Make a plot for every ")
    spinner.setSuffix("file of series.")
    spinner.lineEdit().setReadOnly(True)
    return spinner


def createTimeSeriesChooser(Param_Dict, Misc_Dict):
    """Initialize a spinner with dynamic range to later be changed by maximum
    number of DataSets in a TimeSeries."""
    tooltip = ("Change the number of datasets that are skipped when making "
               "time series profiles")
    spinner = coolSpinBox((1, 10), 1, tooltip)
    spinner.setPrefix("Make Profile for every ")
    spinner.setSuffix("file of series")
    spinner.lineEdit().setReadOnly(True)
    spinner.valueChanged.connect(lambda: Param_Dict["SignalHandler"].getProfOfEveryInput())
    spinner.setDisabled(True)
    Misc_Dict["ProfileSpinner"] = spinner
    return spinner


# %% The PlotAllDialog class for the options of plotting multiple files
class PlotAllDialog(QW.QDialog):
    """A dialog that pops up if the user wants to plot every file of a series.
    Asks the user if he's sure, if he only wants to plot every nth file and if
    he wants to create a movie.
    Params:
        Param_Dict: For receiving information about the series."""
    def __init__(self, Param_Dict):
        super().__init__()
        GUILogger.warn("Do you really want to plot the files with these settings?")
        self.length = len(Param_Dict["DataSeries"])
        self.setWindowFlags(QC.Qt.Window |
                            QC.Qt.CustomizeWindowHint |
                            QC.Qt.WindowTitleHint |
                            QC.Qt.WindowMinimizeButtonHint |
                            QC.Qt.WindowMaximizeButtonHint |
                            QC.Qt.WindowCloseButtonHint)
        self.plotNumber = self.length
        self.onlyEvery = 1
        self.makeMovie = False
        self.setModal(True)  # This way, the user can't interact with the rest
        self.initUi()
        self.signalsConnection()
        self.resize(400, 300)
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle("Options for plotting every file")
        self.show()

    def initUi(self):
        """Initialize all of the ingredients for this UI."""
        # Buttons for closing the window:
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.addButton("Create {} plots".format(self.plotNumber), QW.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QW.QDialogButtonBox.RejectRole)
        self.textBrowser = QW.QTextBrowser()
        text = """<p>Producing a plot for each dataset of the series may,
        depending on your computer specifications and the complexity of the
        plots, take a very long time.</p>
        <p>If you still want to proceed, press the <b>"Create {} plots"</b>-Button
        below. I recommend doing a test plot on just one file before that.</p>
        <p>If you want, you can change how many files are considered and
        whether pictures of the plot are saved so you can make a movie out of
        them.</p>""".format(self.plotNumber)
        self.textBrowser.setHtml(text)
        self.onlyEverySpinner = createOnlyEverySpinner(self.plotNumber)
        self.movieCheckBox = coolCheckBox(text="Save plots as frames for a movie", width=None)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.textBrowser)
        layout.addWidget(self.onlyEverySpinner)
        layout.addWidget(self.movieCheckBox)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def signalsConnection(self):
        """Connects all the signals and emits some of them for a proper start
        """
        self.buttonBox.accepted.connect(self.applyPressed)
        self.buttonBox.rejected.connect(self.cancelPressed)
        self.onlyEverySpinner.valueChanged.connect(self.getOnlyEveryInput)
        self.movieCheckBox.toggled.connect(self.getMovieInput)

    def applyPressed(self):
        """Handles the Button Press of 'Create n plots'"""
        self.Request_Dict = {"OnlyEvery": self.onlyEvery, "Length": self.length,
                             "MakeMovie": self.makeMovie,
                             "PlotNumber": self.plotNumber, "Directory": ""}
        self.accept()

    def cancelPressed(self):
        """Handles the Button press of 'Cancel'"""
        self.reject()

    def getMovieInput(self, state):
        """Save the state of the movieCheckBox"""
        self.makeMovie = state

    def getOnlyEveryInput(self, value):
        """Read out the current value of the spin box and format corresponding
        texts."""
        oldNumber = self.plotNumber
        self.plotNumber = ceil(self.length/value)
        browseText = self.textBrowser.toHtml()
        newText = browseText.replace("Create {} plots".format(oldNumber),
                                     "Create {} plots".format(self.plotNumber))
        self.textBrowser.setHtml(newText)
        self.onlyEvery = value
        self.buttonBox.buttons()[0].setText("Create {} plots".format(self.plotNumber))


# %% The RecalcDialog class for recalculating extrema in time series mode
class RecalcDialog(QW.QDialog):
    """A dialog that pops up if the user wants to calculate the extrema for the
    whole series at once.
    Asks the user whether he/she is sure
    Params:
        Param_Dict: For receiving information about the series."""
    def __init__(self, Param_Dict, axis, parent):
        super().__init__(parent=parent)
        GUILogger.info("Do you want to calculate the global extrema?")
        self.length = len(Param_Dict["DataSeries"])
        self.axis = axis
        self.Param_Dict= Param_Dict
        self.setWindowFlags(QC.Qt.Window |
                            QC.Qt.CustomizeWindowHint |
                            QC.Qt.WindowTitleHint |
                            QC.Qt.WindowMinimizeButtonHint |
                            QC.Qt.WindowMaximizeButtonHint |
                            QC.Qt.WindowCloseButtonHint)
        self.setModal(True)  # This way, the user can't interact with the rest
        self.initUi()
        self.signalsConnection()
        self.resize(200, 100)
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle("Options for extrema calculation")
        self.show()

    def initUi(self):
        """Initialize all of the ingredients for this UI."""
        # Buttons for closing the window:
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.addButton(f"Get extrema of the file selected",
                                 QW.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(f"Get global extrema ({self.length} files)",
                                 QW.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QW.QDialogButtonBox.RejectRole)
        self.textBrowser = QW.QTextBrowser()
        text = """<p>You may calculate the extrema for the whole series if you
        want to. You can also just recalculate them for the file currently
        selected.</p><p><b><font color="red">Warning:</font></b> The former
        process may take a very long time.<br>
        Recalculating the extrema also <b>overwrites the current extrema</b>.
        </p>"""
        self.textBrowser.setHtml(text)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.textBrowser)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def signalsConnection(self):
        """Connects all the signals and emits some of them for a proper start
        """
        hand = self.Param_Dict["SignalHandler"]
        self.buttonBox.buttons()[0].clicked.connect(lambda: hand.calculateExtrema(self.axis))
        self.buttonBox.buttons()[1].clicked.connect(lambda: hand.calculateExtrema(self.axis, series=True))
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.cancelPressed)

    def cancelPressed(self):
        """Handles the Button press of 'Cancel'"""
        self.reject()

# %% The coolAction class and function for creating the MenuBar
class coolAction(QW.QAction):
    """A convenience class to quickly initialize actions for the MenuBar.
    Params:
        name: str: name to be displayed
        shortcut: str: keyboard shortcut for the action. Default: None
        statusTip: str: StatusTip to be displayed in status bar. Default: None
        slot: function object: function to be called when triggered. Defa: None
        parent: QWidget: parent of the action
        helpkey: str if it's a help action
    """
    def __init__(self, name, shortcut=None, statusTip=None, slot=None,
                 parent=None, helpKey=None):
        super().__init__(name, parent=parent)
        if shortcut is not None:
            self.setShortcut(shortcut)
        if statusTip is not None:
            self.setStatusTip(statusTip)
            self.setToolTip(statusTip)
        if slot is not None:
            self.triggered.connect(slot)
        if helpKey is not None:
            self.triggered.connect(lambda: self.openHelpWindow(helpKey))

    def openHelpWindow(self, key):
        """Opens a help window if that's what the action is for"""
        self.helpWindow = HelpWindow(key, parent=self.parent())
        self.helpWindow.show()


def createMenuBar(Window):
    """Creates a menubar on the window Window with all of the needed actions"""
    Action_Dict = {}

    def changeEvalMode(key):
        Window.RadioDict_Dict["EvalMode"][key].setChecked(True)
        Window.openFile()
    Action_Dict["OpenFile"] = coolAction("Open file", "Ctrl+O", "Open a new "
                                         "file", lambda: changeEvalMode("Single file"),
                                         parent=Window)
    Action_Dict["OpenDir"] = coolAction("Open directory", "Ctrl+D", "Open a ne"
                                        "w directory",
                                        lambda: changeEvalMode("Time series"),
                                        parent=Window)
    Action_Dict["CreatePlot"] = coolAction("Create Plot", "Ctrl+Return", "Start"
                                           " evaluation with the current settings",
                                           Window.evaluateSingle, parent=Window)
    Action_Dict["Exit"] = coolAction("Exit", "Ctrl+Q", "Leave the app",
                                     lambda: Window.close(),
                                     parent=Window)
    Action_Dict["ConfigOptions"] = coolAction("Config options", "Ctrl+I",
                                              "Open options for configuration",
                                              Window.openConfigDialog,
                                              parent=Window)
    Action_Dict["LogOptions"] = coolAction("Logging options", "Ctrl+L",
                                           "Open options for logging",
                                           Window.openLoggingOptionsDialog,
                                           parent=Window)
    helpKeys = ["derived fields", "line plots", "slice plots", "phase plots",
                "profile plots", "projection plots"]
    modeKeys = ["Profile", "Line", "Phase", "Slice", "Projection"]

    def changePlotMode(mode):
        """Quickly switch to desired plot mode"""
        if mode in ["Line", "Profile"]:
            Window.RadioDict_Dict["DimMode"]["1D"].setChecked(True)
            Window.RadioDict_Dict["1DOptions"][mode].setChecked(True)
        else:
            Window.RadioDict_Dict["DimMode"]["2D"].setChecked(True)
            Window.RadioDict_Dict["2DOptions"][mode].setChecked(True)
    # Unfortunately a for loop over modeKeys didn't work...
    Action_Dict["Profile"] = coolAction("Profile", "Ctrl+1", "Open profile "
                                        "plot mode",
                                        lambda: changePlotMode("Profile"),
                                        parent=Window)
    Action_Dict["Line"] = coolAction("Line", "Ctrl+2", "Open line plot mode",
                                     lambda: changePlotMode("Line"),
                                     parent=Window)
    Action_Dict["Phase"] = coolAction("Phase", "Ctrl+3", "Open phase plot mode",
                                      lambda: changePlotMode("Phase"),
                                      parent=Window)
    Action_Dict["Slice"] = coolAction("Slice", "Ctrl+4", "Open slice plot mode",
                                      lambda: changePlotMode("Slice"),
                                      parent=Window)
    Action_Dict["Projection"] = coolAction("Projection", "Ctrl+5", "Open "
                                           "projection plot mode",
                                           lambda: changePlotMode("Projection"),
                                           parent=Window)
    for helpKey in helpKeys:
        Action_Dict[helpKey] = coolAction(f"Help on {helpKey}", statusTip="Ope"
                                          f"n help window for {helpKey}",
                                          parent=Window, helpKey=helpKey)
    helpKeys.append("FAQ")
    Action_Dict["FAQ"] = coolAction("FAQ", statusTip="Open answers to some"
                                    "frequently asked questions",
                                    parent=Window, helpKey="FAQ")

    mainMenu = Window.menuBar()
    mainMenu.setStyleSheet("""
QMenuBar {
background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa,
stop: 1 #dadbde); border-style: outset; border-width: 1px; border-radius: 0px;
border-color: gray
}
QMenuBar::item {
    spacing: 3px; /* spacing between menu bar items */
    padding: 1px 4px;
    background: transparent;
    border-radius: 2px;
}
QMenuBar::item:selected { /* when selected using mouse or keyboard */
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
        0 rgb(240, 240, 255), stop: 1 rgb(200, 200, 200))
}
QMenuBar::item:pressed {
    background-color:
    qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
    0 rgb(200, 200, 200), stop: 1 rgb(140, 140, 140))
}
""")
    fileMenu = mainMenu.addMenu("&Program")
    for actionKey in ["OpenFile", "OpenDir", "CreatePlot", "Exit"]:
        fileMenu.addAction(Action_Dict[actionKey])
    plotMenu = mainMenu.addMenu("&Plotting")
    for modeKey in modeKeys:
        plotMenu.addAction(Action_Dict[modeKey])
    optionMenu = mainMenu.addMenu("&Options")
    optionMenu.addAction(Action_Dict["ConfigOptions"])
    optionMenu.addAction(Action_Dict["LogOptions"])
    helpMenu = mainMenu.addMenu("&Help")
    for helpKey in helpKeys:
        helpMenu.addAction(Action_Dict[helpKey])
    return Action_Dict
