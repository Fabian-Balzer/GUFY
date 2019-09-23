# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

A module to include everything concerning the logger:
    - Definition of the handler for the messages
    - Definition of the loggers
    - Creating the TextBrowser widget and connecting yt and GUFY logging to it
    - Definition of the logging options dialog
"""


import PyQt5.QtWidgets as QW
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import logging
from configparser import ConfigParser
from simgui_modules.lineEdits import coolEdit


# %% Logging
class Handler(QC.QObject, logging.Handler):
    """Custom handler with a signal that can be connected to changing the
    text of TextBrowsers or labels.
    Parameters:
        parent: QWidget
        status: Bool in case the handler is connected to the Status bar
    """
    newText = QC.pyqtSignal(object)

    def __init__(self, parent=None, status=False):
        super().__init__(parent)
        super(logging.Handler).__init__()
        self.setLevel(10)  # Debug
        self.status = status

    def emit(self, record):
        """This method is called each time a log message is issued. We take the
        record (including information like source) and turn it into a string
        msg, which is then passed through the signal. Any slot connected to it
        can then display the message."""
        msg = self.formatText(record)
        self.newText.emit(msg)  # <---- emit signal here

    def formatText(self, record):
        """This is a custom formatter since I couldn't properly subclass the
        one from the logging module"""
        if self.status:
            return logging.Formatter().format(record)[:90].split("\n")[0]
        levelno = record.levelno
        if(levelno >= 50):
            color = "DarkRed"
        elif(levelno >= 40):
            color = "Red"
        elif(levelno >= 30):
            color = "Orange"
        elif(levelno >= 20):
            color = "DarkBlue"
        elif(levelno >= 10):
            color = "Green"
        else:
            color = "Green"
        levelname = record.levelname
        if levelname.startswith("Level"):  # for relevant info messages
            levelname = "INFO"
            color = "DarkSlateGray"
        levelname = f'<font color="{color}">{levelname}</font>'
        origin = record.name
        if origin == "GUI":
            origin = "GUFY"  # Because the name was added at a later p.o.t.
        return f"<b>[{origin}-{levelname}]:</b> {record.getMessage()}"


GUILogger = logging.getLogger("GUI")
for handler in GUILogger.handlers:  # This step is very important,
    GUILogger.removeHandler(handler)  # else handlers pile up.
# Create two handlers: One for the TextBrowser, one for the Status bar:
GUIHandler = Handler()
StatusHandler = Handler(status=True)
GUILogger.addHandler(StatusHandler)
GUILogger.addHandler(GUIHandler)
ytLogger = logging.getLogger("yt")
if len(ytLogger.handlers) > 0:
    ytLogger.removeHandler(ytLogger.handlers[0])
# Connect yt logging to handler that will pass everything to the TextBrowser:
ytLogger.addHandler(GUIHandler)


class coolTextBrowser(QW.QTextBrowser):
    """Modified version of TextBrowsers to fit the needs for the logger"""
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(True)
        self.setReadOnly(True)

    def resizeEvent(self, event):
        """Reimplement the resize to always show the latest message"""
        super().resizeEvent(event)
        self.moveCursor(QG.QTextCursor.End)


def createLogger():
    """Creates a logger we can route our info to, and store it in MiscDict.
    Returns:
        logBox: A textBrowser to display logging messages"""
    logBox = coolTextBrowser()
    GUIHandler.newText.connect(logBox.append)  # <-- connect browser to handler
    GUIHandler.newText.connect(lambda: logBox.moveCursor(QG.QTextCursor.End))
    GUIHandler.newText.connect(logBox.repaint)
    return logBox


class LoggingOptionsDialog(QW.QDialog):
    """Small dialog for setting the level of logging. Contains the option
    "configDialog" which is used when it's embedded in the config options.
    Parameters:
        Misc_Dict: For changing the WordCount property of the TextBrowser
        parent: QWidget that can be passed as a parent
        configDialog: Bool: If it should be embedded, we don't need Buttons.
    """
    def __init__(self, Misc_Dict, parent, configDialog=False):
        super().__init__(parent)
        config = ConfigParser()
        config.read("simgui_registry/GUIconfig.ini")
        if configDialog:  # Display the current defaults
            config.read("simgui_registry/GUIconfig.ini")
            self.blockCount = config.getint("Logging", "MaxBlocks")
            self.configString = "<b>default</b> "
        else:  # Display the actual current settings
            self.blockCount = Misc_Dict["LogBox"].document().maximumBlockCount()
            self.configString = ""
        self.Misc_Dict = Misc_Dict
        self.configDialog = configDialog
        self.initUi()
        self.signalsConnection()
        self.setMinimumWidth(350)
        self.setMaximumHeight(600)  # If unexpected long messages occur
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle("Change logging options")
        if not configDialog:
            self.show()

    def initUi(self):
        """Sets up the visual elements of the dialog"""
        layout = QW.QVBoxLayout()
        self.ytSlider, self.ytLabel = self.setUpSlider("yt")
        self.GUISlider, self.GUILabel = self.setUpSlider("GUI")
        layout.addWidget(self.ytSlider)
        layout.addWidget(self.ytLabel)
        layout.addWidget(self.GUISlider)
        layout.addWidget(self.GUILabel)
        blockCountWid = QW.QWidget()
        blockCountLay = QW.QHBoxLayout(blockCountWid)
        blockCountLay.addWidget(QW.QLabel("Maximum number of messages: "))
        validator = QG.QDoubleValidator()
        self.blockCountEdit = coolEdit(str(self.blockCount), "100", "Set maximum number "
                                       "of lines for the logging display", width=None)
        self.blockCountEdit.setValidator(validator)
        blockCountLay.addWidget(self.blockCountEdit)
        blockCountLay.setContentsMargins(3, 3, 3, 3)
        layout.addWidget(blockCountWid)
        if not self.configDialog:  # Only add buttons if not embedded
            self.buttonBox = QW.QDialogButtonBox(self)
            self.buttonBox.addButton("Apply", QW.QDialogButtonBox.AcceptRole)
            self.buttonBox.addButton("Apply and store as default",
                                     QW.QDialogButtonBox.AcceptRole)
            self.buttonBox.addButton("Cancel", QW.QDialogButtonBox.RejectRole)
            layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def signalsConnection(self):
        """Connects the signals to change the settings and emit them with the
        values set before."""
        # Connect the sliders to the text-displaying method. Pass their values.
        self.ytSlider.valueChanged.connect(lambda value: self.changeLabelText(value, self.ytLabel, "yt"))
        self.GUISlider.valueChanged.connect(lambda value: self.changeLabelText(value, self.GUILabel, "GUFY"))
        self.blockCountEdit.textChanged.connect(self.blockCountCheck)
        ytBefore, GUIBefore = getLevelValues(self.configDialog)
        self.ytSlider.setValue(ytBefore)
        self.GUISlider.setValue(GUIBefore)
        self.GUISlider.valueChanged.emit(GUIBefore)
        self.ytSlider.valueChanged.emit(ytBefore)
        if not self.configDialog:
            self.buttonBox.accepted.connect(self.applyPressed)
            self.buttonBox.buttons()[1].clicked.connect(self.storeDefault)
            self.buttonBox.rejected.connect(self.cancelPressed)

    def storeDefault(self):
        """Stores the selected options in the config file."""
        config = ConfigParser()
        config.read("simgui_registry/GUIconfig.ini")
        config["Logging"]["yt"] = str(self.ytInput)
        config["Logging"]["GUI"] = str(self.GUIInput)
        config["Logging"]["MaxBlocks"] = str(self.blockCount)
        with open("simgui_registry/GUIconfig.ini", "w") as configfile:
            config.write(configfile)
        GUILogger.log(29, "Default logging settings have successfully been "
                      "stored.")

    def blockCountCheck(self):
        """Checks if the block count is valid and saves the value at
        self.blockCount"""
        try:
            value = int(self.blockCountEdit.text())
            if value <= 0:
                self.blockCountEdit.setText(str(100))
                value = 100
            self.blockCount = value
        except ValueError:
            self.blockCountEdit.setText(str(self.blockCount))

    def applyPressed(self):
        ytLogger.setLevel(self.ytInput)
        ytLogger.debug('Set level of yt logging to <b><font color="Green">DEBUG</font></b>')
        GUILogger.setLevel(self.GUIInput)
        GUILogger.debug('Set level of GUFY logging to <b><font color="Green">DEBUG</font></b>')
        self.Misc_Dict["LogBox"].document().setMaximumBlockCount(self.blockCount)
        self.accept()

    def cancelPressed(self):
        self.reject()

    def changeLabelText(self, value, label, name):
        """Change the label text of the given label label accordingly"""
        levelText = eval(f"self.get{name}LabelText(value)")
        label.setText(f"Set the {self.configString}minimum <b>{name}</b> "
                      f"logging level to <b>{levelText}</b>.")

    def getGUFYLabelText(self, value):
        """Turns the value into a corresponding level text and returns it."""
        important = False
        if value == 5:
            color, levelname = "DarkRed", "CRITICAL"
        elif value == 4:
            color, levelname = "Red", "ERROR"
        elif value == 3:
            color, levelname = "Orange", "WARNING"
        elif value == 2:
            color, levelname, important = "DarkSlateGray", "INFO", True
        elif value == 1:
            color, levelname = "DarkBlue", "INFO"
        else:
            color, levelname = "Green", "DEBUG"
        if important:
            self.GUIInput = 21
            return f'relevant <font color="{color}">{levelname}</font>'
        else:
            if value < 2:
                value += 1
            self.GUIInput = value*10
            return f'<font color="{color}">{levelname}</font>'

    def getytLabelText(self, value):
        """Turns the value into a corresponding level text and returns it."""
        if value == 4:
            color, levelname = "DarkRed", "CRITICAL"
        elif value == 3:
            color, levelname = "Red", "ERROR"
        elif value == 2:
            color, levelname = "Orange", "WARNING"
        elif value == 1:
            color, levelname = "DarkBlue", "INFO"
        else:
            color, levelname = "Green", "DEBUG"
        self.ytInput = (value+1)*10
        return f'<font color="{color}">{levelname}</font>'

    def setUpSlider(self, name):
        """Sets up the settings Sliders for the options dialog and returns them
        plus a Label"""
        slider = QW.QSlider(QC.Qt.Horizontal)
        if name == "yt":
            slider.setRange(0, 4)
        else:
            slider.setRange(0, 5)
        slider.setTickPosition(QW.QSlider.TicksBelow)
        slider.setTickInterval(1)
        slider.setToolTip(F"Select the information level for {name}logging")
        return slider, QW.QLabel()


def getLevelValues(configDialog):
    """Retrieves the current yt and GUI logger level values and turns them to
    a range between 0 and 5.
    Parameters:
        configDialog: Bool: Whether the values should be retrieved from default"""
    config = ConfigParser()
    config.read("simgui_registry/GUIconfig.ini")
    if configDialog:
        ytLevel = config.getint("Logging", "yt")//10 - 1
        GUILevel = config.getint("Logging", "GUI")
    else:
        ytLevel = ytLogger.getEffectiveLevel()//10 - 1
        GUILevel = GUILogger.getEffectiveLevel()
    GUILogger.debug(f"Received initial values yt: {ytLevel} and GUI: {GUILevel}")
    if GUILevel >= 30:
        GUILevel //= 10
    elif 20 < GUILevel < 30:
        GUILevel = 2
    else:
        GUILevel = GUILevel//10 - 1
    GUILogger.debug(f"Set the values to yt: {ytLevel} and GUI: {GUILevel}")
    return ytLevel, GUILevel

