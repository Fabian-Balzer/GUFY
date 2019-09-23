# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

A module containing some options for configuring everything.
"""


import inspect
import os
import logging
from configparser import ConfigParser, NoOptionError
import PyQt5.QtWidgets as QW
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
from yt import YTQuantity
from simgui_modules.buttons import coolButton
from simgui_modules.checkBoxes import coolCheckBox, createAnnotationBoxes
from simgui_modules.comboBoxes import createTimeQuantityBox, createWeightBoxes
from simgui_modules.lineEdits import createColorSchemeEdit, coolEdit, \
    validColors
from simgui_modules.logging import LoggingOptionsDialog

GUILogger = logging.getLogger("GUI")
ytLogger = logging.getLogger("yt")
# Load the configuration file
config = ConfigParser()
config.read("simgui_registry/GUIconfig.ini")


class ConfigDialog(QW.QDialog):
    """A Dialog where the user can set all configuration options.
    Parameters:
        Param_Dict: To receive initial conditions and store the outputs
        parent: QWidget: The Dialogs' parent"""
    def __init__(self, Param_Dict, Misc_Dict, parent):
        super().__init__(parent)
        self.Param_Dict = Param_Dict
        self.Misc_Dict = Misc_Dict
        self.Config_Dict = {}
        self.setWindowFlags(  # Set minimize, maximize and close button
                            QC.Qt.Window |
                            QC.Qt.CustomizeWindowHint |
                            QC.Qt.WindowTitleHint |
                            QC.Qt.WindowMinimizeButtonHint |
                            QC.Qt.WindowMaximizeButtonHint |
                            QC.Qt.WindowCloseButtonHint
                            )
        self.initUi()
        self.signalsConnection()
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle("Set up configuration")
        self.show()

    def initUi(self):
        """Initialize the visual elements of the user interface"""
        # Buttons for closing the window:
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.addButton("Save", QW.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QW.QDialogButtonBox.RejectRole)
        self.textBrowser = QW.QTextBrowser()
        text = """Here you can set up the default settings the GUI is started
        with.<br>Except for the home directory, <b>these options will not
        change the current session of the GUI</b>.<br>
        The current logging settings can be changed by pressing <i>CTRL+L</i>.
        """
        self.textBrowser.setHtml(text)
        self.textBrowser.setMinimumWidth(150)
        self.homeDir = config["Path"]["homedir"]
        self.directoryLabel = QW.QLabel(f'Current home directory:\n{self.homeDir}')
        self.directoryButton = coolButton(text="Set home directory",
                                          tooltip="Set the new home directory")
        layout = QW.QGridLayout()
        layout.addWidget(self.textBrowser, 0, 0)
        layout.addWidget(self.createCheckBoxes(), 0, 1)
        layout.addWidget(self.createLoggings(), 2, 0)
        layout.addWidget(self.createMiscs(), 2, 1)
        layout.addWidget(self.directoryLabel, 3, 0, 1, 2)
        layout.addWidget(self.directoryButton, 4, 0, 1, 2)
        layout.addWidget(self.buttonBox, 5, 1)
        self.setLayout(layout)

    def createCheckBoxes(self):
        """Creates a group box with all relevant Checkboxes on it, and stores
        them in CheckBox_Dict"""
        wid = QW.QGroupBox("CheckBox defaults")
        mainLayout = QW.QHBoxLayout(wid)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        annoWid = QW.QWidget()
        annoLayout = QW.QVBoxLayout(annoWid)
        annoLayout.setSpacing(3)
        annoLayout.addWidget(QW.QLabel("Annotations: "))
        annoKeys = ["Timestamp", "Scale", "Grid",
                    "VelVectors", "VelStreamlines",
                    "MagVectors", "MagStreamlines", "Contour", "Particleanno",
                    "LineAnno"]
        annoBoxes = createAnnotationBoxes(width=None, defaultString="default ")
        self.CheckBox_Dict = dict(zip(annoKeys, annoBoxes))
        for key in sorted(annoKeys):
            annoLayout.addWidget(self.CheckBox_Dict[key])
        annoLayout.addStretch(1)
        miscWid = QW.QWidget()
        miscLayout = QW.QVBoxLayout(miscWid)
        miscLayout.setSpacing(3)
        miscLayout.addWidget(QW.QLabel("Miscellaneous: "))
        otherKeys = ["XLog", "YLog", "ZLog", "SetAspect", "QuitDialog"]
        otherTexts = ["Log horizontal axis", "Log vertical axis",
                      "Log color bar axis",
                      "Ignore aspect ratio",
                      "Warn me before quitting"]
        for key, text in zip(otherKeys, otherTexts):
            checkBox = coolCheckBox(text, f"Toggle {text.lower()} default",
                                    width=None)
            self.CheckBox_Dict[key] = checkBox
            if key == "QuitDialog":
                miscLayout.addStretch(1)
            miscLayout.addWidget(checkBox)
        for key in self.CheckBox_Dict.keys():
            self.CheckBox_Dict[key].setChecked(config.getboolean("CheckBoxes", key))
        mainLayout.addWidget(annoWid)
        mainLayout.addWidget(miscWid)
        wid.setMinimumWidth(400)
        return wid

    def createLoggings(self):
        """Creates a group box for logging options"""
        wid = QW.QGroupBox("Logging defaults")
        layout = QW.QVBoxLayout(wid)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 3, 3, 3)
        self.LogDialog = LoggingOptionsDialog(self.Misc_Dict, parent=self,
                                              configDialog=True)
        layout.addWidget(self.LogDialog)
        return wid

    def createMiscs(self):
        """Creates a group box with all relevant Misc items on it, and stores
        them in Misc_Dict"""
        wid = QW.QGroupBox("Miscellaneous defaults")
        layout = QW.QFormLayout(wid)
        layout.setSpacing(3)
        self.Misc_Dict = {}
        keys = ["gridunit", "colorscheme", "timequantity", "weightfield"]
        self.Misc_Dict["colorscheme"] = createColorSchemeEdit(width=None)
        self.Misc_Dict["colorscheme"].setText(config["Misc"]["colorscheme"])
        self.Misc_Dict["colorscheme"].setToolTip("Set the default color scheme")
        self.Misc_Dict["gridunit"] = coolEdit(config["Misc"]["gridunit"], "au",
                                              "Set the length unit default for"
                                              " the GUI", width=None)
        self.Misc_Dict["timequantity"] = createTimeQuantityBox(width=None)
        self.Misc_Dict["timequantity"].setCurrentText(config["Misc"]["timequantity"])
        self.Misc_Dict["weightfield"] = createWeightBoxes("Color", width=None)
        self.Misc_Dict["weightfield"].setToolTip("Select weight field default for "
                                                 "phase, profile and projection plots")
        self.Misc_Dict["weightfield"].setCurrentText(config["Misc"]["weightfield"])
        texts = ["Color scheme: ", "Length unit: ", "Time quantity: ",
                 "Weight field: "]
        keys = ["colorscheme", "gridunit", "timequantity", "weightfield"]
        for text, key in zip(texts, keys):
            layout.addRow(text, self.Misc_Dict[key])
        return wid
        

    def signalsConnection(self):
        """Connect the signals of accept and cancelbutton"""
        self.buttonBox.accepted.connect(self.saveSettings)
        self.buttonBox.rejected.connect(self.cancelPressed)
        self.directoryButton.clicked.connect(self.getHomeDir)
        self.Misc_Dict["colorscheme"].textChanged.connect(self.getColorInput)
        self.Misc_Dict["gridunit"].textChanged.connect(self.getGridInput)
        self.Misc_Dict["timequantity"].currentIndexChanged.connect(lambda: self.getComboInput("timequantity"))
        self.Misc_Dict["weightfield"].currentIndexChanged.connect(lambda: self.getComboInput("weightfield"))
        self.CheckBox_Dict["Timestamp"].toggled.connect(lambda state: self.getStateInput("Timestamp", state))
        self.CheckBox_Dict["Scale"].toggled.connect(lambda state: self.getStateInput("Scale", state))
        self.CheckBox_Dict["Grid"].toggled.connect(lambda state: self.getStateInput("Grid", state))
        self.CheckBox_Dict["Contour"].toggled.connect(lambda state: self.getStateInput("Contour", state))
        self.CheckBox_Dict["VelVectors"].toggled.connect(lambda state: self.getStateInput("VelVectors", state))
        self.CheckBox_Dict["VelStreamlines"].toggled.connect(lambda state: self.getStateInput("VelStreamlines", state))
        self.CheckBox_Dict["MagVectors"].toggled.connect(lambda state: self.getStateInput("MagVectors", state))
        self.CheckBox_Dict["MagStreamlines"].toggled.connect(lambda state: self.getStateInput("MagStreamlines", state))
        self.CheckBox_Dict["LineAnno"].toggled.connect(lambda state: self.getStateInput("LineAnno", state))
        self.CheckBox_Dict["XLog"].toggled.connect(lambda state: self.getStateInput("XLog", state))
        self.CheckBox_Dict["YLog"].toggled.connect(lambda state: self.getStateInput("YLog", state))
        self.CheckBox_Dict["ZLog"].toggled.connect(lambda state: self.getStateInput("ZLog", state))
        self.CheckBox_Dict["SetAspect"].toggled.connect(lambda state: self.getStateInput("SetAspect", state))
        self.CheckBox_Dict["QuitDialog"].toggled.connect(lambda state: self.getStateInput("QuitDialog", state))

    def getStateInput(self, key, state):
        """Store the CheckBox input as a string that can be saved in the config
        file."""
        boolString = "no"
        if state:
            boolString = "yes"
        self.Config_Dict["CheckBoxes_" + key] = boolString

    def getColorInput(self, text):
        """Read out the input of the color scheme and give feedback if it is
        valid"""
        if text not in validColors:
            self.Misc_Dict["colorscheme"].turnTextRed()
            self.Config_Dict["Misc_colorscheme"] = "viridis"
        else:
            self.Misc_Dict["colorscheme"].turnTextBlack()
            self.Config_Dict["Misc_colorscheme"] = text

    def getComboInput(self, key):
        """Read out the input of the time quantity"""
        self.Config_Dict[f"Misc_{key}"] = self.Misc_Dict[key].currentText()

    def getGridInput(self, text):
        """Read out grid unit input and give feedback"""
        # reference unit
        fieldUnit = YTQuantity(1, "au").units
        from yt.units.unit_object import UnitParseError
        lineEdit = self.Misc_Dict["gridunit"]
        try:
            textUnit = YTQuantity(1, text).units
            if fieldUnit.same_dimensions_as(textUnit):
                lineEdit.turnTextBlack()
                newUnit = lineEdit.text()
            else:
                lineEdit.turnTextRed()
                newUnit = str(fieldUnit)
        except (UnitParseError, AttributeError, TypeError):
            lineEdit.turnTextRed()
            newUnit = str(fieldUnit)
        self.Config_Dict["Misc_gridunit"] = newUnit

    def getHomeDir(self):
        """Opens a dialog to receive the home directory"""
        directory = QW.QFileDialog.getExistingDirectory(self, "Select a home "
                                                        "directory",
                                                        self.homeDir)
        if directory != '':
            self.homeDir = directory
            self.directoryLabel.setText(f"Current home directory:\n{directory}")

    def saveSettings(self):
        """Handles the saving operations"""
        config["Path"]["homedir"] = self.homeDir
        config["Logging"]["yt"] = str(self.LogDialog.ytInput)
        config["Logging"]["GUI"] = str(self.LogDialog.GUIInput)
        config["Logging"]["MaxBlocks"] = str(self.LogDialog.blockCount)
        if not self.Param_Dict["isValidFile"]:  # only if no file is loaded
            self.Param_Dict["Directory"] = self.homeDir
            self.parent().Status_Dict["Dir"].setText(self.homeDir)
        for key in self.Config_Dict.keys():
            group = key.split("_")[0]
            subkey = key.split("_")[1]
            config[group][subkey] = self.Config_Dict[key]
        saveConfigOptions(log=True)
        self.accept()

    def cancelPressed(self):
        """Handles the Button press of 'Cancel'"""
        GUILogger.info("No settings saved.")
        self.reject()


def getHomeDirectory():
    """Checks whether a home directory is stored in the config file. If not,
    determines the directory the GUI is started from and saves it as the home
    directory.
    Returns:
        directory: str: The working directory"""
    directory = config["Path"]["homedir"]
    if directory == "" or not os.path.isdir(directory):
        # https://stackoverflow.com/questions/3718657/how-to-properly-determine-current-script-directory
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        moduleDir = os.path.dirname(os.path.abspath(filename))
        # some string formatting to remove the last bit:
        directory = "\\".join(moduleDir.split("\\")[:-1])
        GUILogger.info("Couldn't locate home directory. Default directory is "
                       "set to the directory the program was started in.")
    return directory


def loadConfigOptions(Window):
    """Sets the widgets according to the settings given through the config
    file"""
    text = config["Misc"]["colorscheme"]
    Window.Edit_Dict["ColorScheme"].setText(text)
    Window.Edit_Dict["ColorScheme"].setPlaceholderText(text)
    text = config["Misc"]["gridunit"]
    Window.Edit_Dict["GridUnit"].setText(text)
    Window.Edit_Dict["GridUnit"].setPlaceholderText(text)
    text = config["Misc"]["timequantity"]
    Window.ComboBox_Dict["TimeQuantity"].setCurrentText(text)
    text = config["Misc"]["weightfield"]
    Window.ComboBox_Dict["YWeight"].setCurrentText(text)
    Window.Misc_Dict["LogBox"].document().setMaximumBlockCount(config.getint("Logging", "MaxBlocks"))
    GUILogger.setLevel(config.getint("Logging", "GUI"))
    ytLogger.setLevel(config.getint("Logging", "yt"))
    GUILogger.info("Logs and additional Information will be displayed here.")
    GUILogger.log(29, "You can <b>change the logging level</b> by pressing <i>ctrl + L</i> or in the <i>Options</i> menu.")
    GUILogger.info("Please open a (FLASH-)simulation file or a time series to get started.")
    for key in Window.CheckBox_Dict.keys():
        try:
            Window.CheckBox_Dict[key].setChecked(config.getboolean("CheckBoxes", key))
        except NoOptionError:
            pass


def saveConfigOptions(log=False):
    """Convenience method to store the config options in the config file."""
    with open("simgui_registry/GUIconfig.ini", "w") as configfile:
        config.write(configfile)
    if log:
        GUILogger.log(29, "New configuration settings have successfully been stored.")
