#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

A program used to visualize FLASH Code simulation data using yt.
Based on the project math2.py by Jannik Schilling.

The body of the MainWindow class is structured as follows:
    - Initialization methods
    - Methods for file opening
    - Methods for series opening
    - Methods for file and series evaluation
    - Methods for dialog opening (derived fields, script writing etc.)
    - Methods for line drawing functionality
    - Other methods (testing and close event) in alphabetical order
At the very end, the functions to actually start the application are written.
"""
import sys
import os
from configparser import ConfigParser
import yt
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
from simgui_modules import dictionaries
from simgui_modules import utils as sut
from simgui_modules.plotWindow import PlotWindow
from simgui_modules.layouts import createAllWidgets
from simgui_modules.labels import createAllLabels
from simgui_modules.buttons import createAllButtons
from simgui_modules.checkBoxes import createAllCheckBoxes
from simgui_modules.signalHandler import fillDataSetDict, SignalHandler, \
    updateLabels
from simgui_modules.comboBoxes import createAllComboBoxes
from simgui_modules.lineEdits import createAllEdits
from simgui_modules.radioButtonDicts import createAllRadioDicts
from simgui_modules.logging import createLogger, LoggingOptionsDialog, \
    GUILogger
from simgui_modules.additionalWidgets import createAllStatusInfo, \
    createDataSetSlider, createMenuBar, createTimeSeriesChooser, \
    PlotAllDialog, setUpWidgets, RecalcDialog
from simgui_modules import derivedFieldWidget as sder
from simgui_modules import helpWindows as shel
from simgui_modules.threading import ProgressDialog
from simgui_modules.scriptWriter import WriteToScriptDialog
from simgui_modules.configureGUI import ConfigDialog, \
    getHomeDirectory, loadConfigOptions


# Import useful exceptions
from yt.utilities.exceptions import YTOutputNotIdentified
__version__ = "1.0.2"


# %% Application starts here
class GUFYMainWindow(QW.QMainWindow):
    """The MainWindow everything is hosted on. All of the widgets are stored
    in dictionaries for easy acces (see createDictionaries).
    The body is structured as follows:
        - Initialization methods
        - Methods for file opening
        - Methods for series opening
        - Methods for file and series evaluation
        - Methods for dialog opening (derived fields, script writing etc.)
        - Methods for line drawing functionality
        - Other methods (testing and close event) in alphabetical order
    """
    def __init__(self):
        super().__init__()
        self._main = QW.QWidget()
        self.setCentralWidget(self._main)
        self.initUi()

    # %% Initialization methods
    def initUi(self):
        """Contains all the actions needed for intitializing the interface.
        """
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle("GUFY - GUI for FLASH Code simulations based on yt")
        height = int(QW.QDesktopWidget().screenGeometry(-1).height()*0.85)
        width = int(QW.QDesktopWidget().screenGeometry(-1).width()*0.7)
        self.setGeometry(0, 0, width, height)
        self.move(20, 20)

        self.createAllDicts()
        self.connectAllButtons()

        # Figure (needs to be introduced after the signal handler has been set up,
        # because we want to pass references to it)
        # This single plot window is only responsible for single file plots.
        plotWindow = PlotWindow(self.Status_Dict, parent=self._main)
        self.Param_Dict["DataSetPlotWindow"] = plotWindow
        self.Param_Dict["CurrentPlotWindow"] = plotWindow
        loadConfigOptions(self)  # Restore the desired config settings

        self.Wid_Dict["TopLayout"].addWidget(self.Param_Dict["DataSetPlotWindow"], 0, 0)  # top left for Plot
        self.Param_Dict["SignalHandler"].makeInitialCopy()
        self.Param_Dict["SignalHandler"].changeEvalMode()

        self.setUp()
        self.Action_Dict = createMenuBar(self)

    def createAllDicts(self):
        """This function calls all of the dictionary-creating and
        dictionary-filling functions. These dictionaries are used to store the
        widgets of the GUI in a central place.
        The parameter dictionary (self.Param_Dict) is the place where all
        temporary data is stored. For further details look at their creation
        functions."""
# DICT CREATION
# Data storage:
        self.Param_Dict = dictionaries.createParam_Dict()
        # here you may toggle testing mode - you will need to set the testfiles
        self.Param_Dict["TestingMode"] = False
# Buttons:
        self.Button_Dict = dictionaries.createButton_Dict()
# CheckBoxes:
        self.CheckBox_Dict = dictionaries.createCheckBox_Dict()
# ComboBoxes:
        self.ComboBox_Dict = dictionaries.createComboBox_Dict()
# LineEdits:
        self.Edit_Dict = dictionaries.createEdit_Dict()
# Labels:
        self.Label_Dict = dictionaries.createLabel_Dict()
# Misc: These widgets didn't fit in any other category.
        self.Misc_Dict = dictionaries.createMisc_Dict()
# RadioButtons (stored in separate dictionaries):
        self.RadioDict_Dict = dictionaries.createRadioDict_Dict()
# Status:
        self.Status_Dict = dictionaries.createStatus_Dict()
# Widgets: Mainly little BoxLayouts
        self.Wid_Dict = dictionaries.createWid_Dict()
        # Now that they are created, they can be filled step by step
        # (Filling and creation need to be separate because of references)
    # DICT FILLING
        self.Param_Dict["SignalHandler"] = SignalHandler(self)
        self.Param_Dict["Directory"] = getHomeDirectory()
    # Status
        createAllStatusInfo(self.Param_Dict, self.Status_Dict)
        self.setStatusBar(self.Status_Dict["Bar"])
    # Slider
        createDataSetSlider(self.Param_Dict, self.Misc_Dict)
    # Spinner
        createTimeSeriesChooser(self.Param_Dict, self.Misc_Dict)
    # ComboBoxes
        createAllComboBoxes(self.Param_Dict, self.ComboBox_Dict)
    # LineEdits
        createAllEdits(self.Param_Dict, self.Edit_Dict)
    # RadioButton group dictionaries
        createAllRadioDicts(self._main, self.Param_Dict, self.RadioDict_Dict)
    # Buttons
        createAllButtons(self.Button_Dict)
    # CheckBoxes
        createAllCheckBoxes(self.Param_Dict, self.CheckBox_Dict)
    # Labels
        createAllLabels(self.Label_Dict)
    # Logger
        self.Misc_Dict["LogBox"] = createLogger()
    # Widgets
        createAllWidgets(self)

    def connectAllButtons(self):
        """Convenience method to connect all of the buttons to their slots"""
        self.Button_Dict["Open"].clicked.connect(self.openFile)
        self.Button_Dict["Evaluate"].clicked.connect(self.evaluateSingle)
        self.Button_Dict["PlotAll"].clicked.connect(self.openPlotAllDialog)
        self.Button_Dict["QuickCart"].clicked.connect(lambda: self.loadTestFile("Cartesian"))
        self.Button_Dict["QuickCyli"].clicked.connect(lambda: self.loadTestFile("Cylindrical"))
        self.Button_Dict["QuickSeries"].clicked.connect(self.loadTestSeries)
        self.Button_Dict["AddDerField"].clicked.connect(self.openDerFieldDialog)
        self.Button_Dict["WriteScript"].clicked.connect(self.openWriteScriptDialog)
        self.Button_Dict["MakeLinePlot"].clicked.connect(self.startLine)
        self.Button_Dict["PrintDict"].clicked.connect(lambda: sut.printParam_Dict(self.Param_Dict))
#        self.Button_Dict["PrintDict"].clicked.connect(lambda: print(config["Logging"]["yt"]))

    def setUp(self):
        """Goes through all the methods to set up default the screen
        appropriately"""
        sut.resetExtrema(self.Param_Dict, self.Edit_Dict,
                         self.Button_Dict, self.Label_Dict,
                         self.ComboBox_Dict, self)
        self.Param_Dict["SignalHandler"].changeDimensions()

    # %% Methods for file opening and loading (the first one differentiates file/series)
    def openFile(self):
        """Opens a file dialogue and promts the user to add a file or
        directory, depending on the mode selected in Param_Dict["EvalMode"].
        Also tries to load the file using yt.
        """
        if self.Param_Dict["EvalMode"] == "Single":
            # Create a window that contains dialogue for opening file
            GUILogger.info("Opening file in single file mode")
            self.testValidFile()
        else:
            # Create a window that contains dialogue for opening directory
            GUILogger.info("Opening file in time series mode")
            self.testValidSeries()

    def testValidFile(self):
        """Promts the user to enter a file name. If yt can't load it, display
        an error message and try again.
        returns:
            True if load was successful
            False if user cancels before successful load
        """
        filename = QW.QFileDialog.getOpenFileName(self, "Select a simulation file", 
                                                  self.Param_Dict["Directory"],
                                                  "All files (*)")[0]
        if filename != '':
            try:
                # SingleDataSet is there so we can go back to a single dataset
                # if the user loaded one.
                self.Param_Dict["SingleDataSet"] = self.loadFile(filename)
                self.Param_Dict["CurrentDataSet"] = self.Param_Dict["SingleDataSet"]
                self.Param_Dict["Seriesname"] = ""
                self.Param_Dict["Filename"] = filename
                self.Status_Dict["Series"].setText(self.Param_Dict["Seriesname"])
                self.Param_Dict["isValidFile"] = True
                self.Param_Dict["isValidSeries"] = False
                self.setUpFile()
                return
            except YTOutputNotIdentified:
                sut.alertUser("Couldn't load this file. Please try again")
                # Ask the user to enter another series name.
                # If he cancels, pass.
                self.testValidFile()
        else:
            GUILogger.warning("Couldn't load file. Click 'Open File' to start over.")
            return

    def loadFile(self, filename):
        """Handles loading a given file filename.
        Also changes the current working directory
        self.Param_Dict["Directory"].
        Parameters:
            filename: path of the file to load
        returns:
            ds: yt DataSet object
        """
        # Perform a reverse split to receive the directory and name separately
        directory, name = filename.rsplit('/', 1)
        self.Status_Dict["Dir"].setText(directory)
        self.Status_Dict["File"].setText('File: ' + name)
        self.Param_Dict["Directory"] = directory
        ds = yt.load(filename)
        GUILogger.info(f"Loading file '{name}'...")
        return ds

    def setUpFile(self, testmode=""):
        """When the file is given, make it ready for evaluation by updating
        the fields for the axes and calculating their min and maxes.
        Parameters:
            testmode: argument given when called through the buttons to test
        """
        if self.Param_Dict["isValidFile"]:
            self.Param_Dict["SignalHandler"].changeEvalMode()
            self.Button_Dict["MakeLinePlot"].hide()
            GUILogger.info("Scanning file for relevant fields...")
            # Update Geometry and hide the widgets that would cause errors
            sut.updateGeometry(self.Param_Dict, self.CheckBox_Dict,
                               self.RadioDict_Dict, self.Edit_Dict,
                               self.Label_Dict)
            # Update the comboBoxes according to entries in field lists
            try:
                sut.updateFields(self.Param_Dict, self.ComboBox_Dict)
            except Exception:
                return
            sut.resetExtrema(self.Param_Dict, self.Edit_Dict,
                             self.Button_Dict, self.Label_Dict,
                             self.ComboBox_Dict, self)
            self.Param_Dict["SignalHandler"].getOtherUnitInput("Grid")
            self.Param_Dict["SignalHandler"].setPlotOptions()
            updateLabels(self.Param_Dict, self.Label_Dict)
            GUILogger.log(29, f"Loaded '{self.Param_Dict['Filename'].split('/')[-1]}'.")
            GUILogger.info("It is now ready for plotting.")
            sut.refreshWidgets(self.Edit_Dict, self.ComboBox_Dict)

    # %% Methods for series opening and loading
    def testValidSeries(self):
        """Promts the user to enter a directory name. After one has been
        chosen, prompt for a series name. If yt can't load it, display
        an error message and try again.
        """
        directory = QW.QFileDialog.getExistingDirectory(self, "Select a directory with your series in it",
                                                        self.Param_Dict["Directory"])
        if directory != '':
            # Information on DataSetSeries object:
            # http://yt-project.org/doc/reference/api/yt.data_objects.time_series.html#yt.data_objects.time_series.DataSetSeries
            ts = self.loadSeries(directory)
            if ts is None:
                return
            try:
                GUILogger.info(f"This series includes {len(ts)} files.")
#                ts = [yt.load(filename) for filename in ts._pre_outputs]
                self.Param_Dict["DataSeries"] = ts
                self.setUpSeries()
            except TypeError:
                self.RadioDict_Dict["EvalMode"]["Single file"].setChecked(True)
                self.Param_Dict["SingleDataSet"] = ts
                GUILogger.warning("Only a single file has been selected. Changing to single file mode.")
                self.Param_Dict["Filename"] = self.Param_Dict["Seriesname"]
                self.Param_Dict["Seriesname"] = ""
                self.Status_Dict["Series"].setText(self.Param_Dict["Seriesname"])
                self.Status_Dict["File"].setText(self.Param_Dict["Seriesname"])
                self.Param_Dict["isValidFile"] = True
                self.Param_Dict["isValidSeries"] = False
                self.setUpFile()

    def loadSeries(self, directory):
        """Handles loading a given series in a directory.
        Also changes the current working directory
        self.Param_Dict["Directory"]
        Parameters:
            directory: path of the series
        returns:
            ts: yt DataSetSeries object
        """
        GUILogger.info(f"{directory} is directory for series mode")
        self.Status_Dict["Dir"].setText(directory)
        self.Param_Dict["Directory"] = directory
        ok = self.askSeriesName()
        if ok:
            try:
                GUILogger.info(f"Loading series '{self.Param_Dict['Seriesname']}'...")
                ts = yt.load(directory + '/' + self.Param_Dict["Seriesname"])
                self.Param_Dict["Filename"] = ""
                self.Status_Dict["File"].setText(self.Param_Dict["Filename"])
                self.Param_Dict["isValidSeries"] = True
                self.Param_Dict["isValidFile"] = True
                return ts
            except YTOutputNotIdentified:
                sut.alertUser("Couldn't load this series. Please try again")
                # Ask the user to enter another series name.
                # If he cancels, pass.
                return self.loadSeries(directory)
        else:
            GUILogger.warning("Couldn't load series.")
            GUILogger.log(29, "Try replacing the last digits of your series with "
                          "questionmarks or import all files of the directory "
                          "by using *")
            return None

    def askSeriesName(self):
        """Promts the user to enter a seriesname and saves it to
        self.Param_Dict["Seriesname"].
        Tries to make suggestions using the first file in the directory.
        returns:
            ok: True if user enters ok, False if user cancels
        """
        possibleNames = []
        # create a completer with the strings in the column as model
        directory = self.Param_Dict["Directory"]
        for file in os.listdir(directory):
            if os.path.isfile(f"{directory}/{file}") and not file.endswith(".py"):
                possibleNames.append(file)
        possibleNames.append("*")
        seriesname, ok = QW.QInputDialog.getItem(self, "Name of the series",
                                                 f"Directory:\n{directory}\n\n"
                                                 "Please provide the name of "
                                                 "the series.\n"
                                                 "Hint: Replace the last "
                                                 "numbers with questionmarks.",
                                                 possibleNames)
        if ok:
            self.Param_Dict["Seriesname"] = str(seriesname)
            self.Status_Dict["Series"].setText('Series:' + self.Param_Dict["Seriesname"])
        else:
            self.Param_Dict["Seriesname"] = 'No series selected'
            self.Status_Dict["Series"].setText('No series selected')
        return ok

    def setUpSeries(self):
        """When the series is given, make it ready for evaluation by updating
        fields for the axes"""
        if self.Param_Dict["isValidSeries"]:
            self.Param_Dict["SignalHandler"].changeEvalMode()
            self.Status_Dict["Status"].setText("Series ready to evaluate.")
            self.Button_Dict["MakeLinePlot"].hide()
            GUILogger.info("Scanning the first file for relevant fields...")
            # Update Geometry and hide the widgets that would cause errors
            self.Param_Dict["CurrentDataSet"] = self.Param_Dict["DataSeries"][0]
            sut.updateGeometry(self.Param_Dict, self.CheckBox_Dict,
                               self.RadioDict_Dict, self.Edit_Dict,
                               self.Label_Dict)
            # Update the comboBoxes according to entries in field lists
            try:
                sut.updateFields(self.Param_Dict, self.ComboBox_Dict)
            except Exception:
                return
            sut.resetExtrema(self.Param_Dict, self.Edit_Dict,
                             self.Button_Dict, self.Label_Dict,
                             self.ComboBox_Dict, self)
            self.Param_Dict["SignalHandler"].getOtherUnitInput("Grid")
            fillDataSetDict(self.Param_Dict, self.Status_Dict,
                            self.Wid_Dict["TopLayout"], self._main)
            setUpWidgets(self.Param_Dict, self.CheckBox_Dict,
                         self.Misc_Dict)
            updateLabels(self.Param_Dict, self.Label_Dict)
            self.Param_Dict["SignalHandler"].setPlotOptions()
            sut.refreshWidgets(self.Edit_Dict, self.ComboBox_Dict)

    # %%Methods for file and series evaluation:
    def evaluateSingle(self):
        """Passes the evaluation of data to a ProgressDialog"""
        if self.Param_Dict["EvalMode"] == "Single" and not self.Param_Dict["isValidFile"]:
            GUILogger.error("Evaluation stopped. Please open valid file first.")
            return
        if self.Param_Dict["EvalMode"] == "Series" and not self.Param_Dict["isValidSeries"]:
            GUILogger.error("Evaluation stopped. Please open valid directory "
                            "first and enter valid series name.")
            return
        GUILogger.info("Evaluation started. Checking for missing extrema...")
        sut.checkExtremaForPlot(self.Param_Dict)
        self.progressDialog = ProgressDialog(self.Param_Dict, self, mode="PlotSingle")
        self.progressWorker.finished.connect(self.giveSingleFeedback)

    def giveSingleFeedback(self, success):
        """Gives feedback on wether the plot was successful.
        Shows the MakeLinePlot button upon successful plotting if the
        conditions are met"""
        mode = self.Param_Dict["PlotMode"]
        if success:
            GUILogger.log(29, f"{mode} plot successful.")
            cart = self.Param_Dict["Geometry"] == "cartesian"
            aligned = self.Param_Dict["NormVecMode"] == "Axis-Aligned"
            slcproj = mode in ["Slice", "Projection"]
            if cart and slcproj and aligned:
                self.Button_Dict["MakeLinePlot"].show()

    def evaluateMultiple(self, Request_Dict):
        """Passes the evaluation of multiple plots to a ProgressDialog."""
        self.Param_Dict["OnlyEvery"] = Request_Dict["OnlyEvery"]
        if Request_Dict["MakeMovie"]:
            Request_Dict["Directory"] = sut.setUpMovieFolder(self.Param_Dict)
            if not Request_Dict["Directory"]:
                return
        GUILogger.info("Evaluation started. Checking for missing extrema...")
        sut.checkExtremaForPlot(self.Param_Dict)
        self.progressDialog = ProgressDialog(self.Param_Dict, self,
                                             mode="PlotAll",
                                             Request_Dict=Request_Dict,
                                             slider=self.Misc_Dict["SeriesSlider"])
        self.progressWorker.finished.connect(self.giveMultipleFeedback)

    def giveMultipleFeedback(self, success, directory):
        """Gives feedback on wether multiple plots were successful."""
        mode = self.Param_Dict["PlotMode"]
        if success:
            GUILogger.log(29, f"{mode} plots successful.")
            if directory != "":
                GUILogger.log(29, f"The pictures have been saved to <b>{directory}</b>.")
            cart = self.Param_Dict["Geometry"] == "cartesian"
            aligned = self.Param_Dict["NormVecMode"] == "Axis-Aligned"
            slcproj = mode in ["Slice", "Projection"]
            if cart and slcproj and aligned:
                self.Button_Dict["MakeLinePlot"].show()

    # %% Methods for dialog opening (derived fields, script writing etc.):
    def openDerFieldDialog(self):
        self.fDialog = sder.AskFieldDialog(self.Param_Dict["ZFields"],
                                           self.Param_Dict["CurrentDataSet"],
                                           self)
        self.fDialog.accepted.connect(lambda: sder.getDerFieldInfo(self.Param_Dict,
                                                                   self.ComboBox_Dict,
                                                                   self.Misc_Dict,
                                                                   self.fDialog))

    def openWriteScriptDialog(self):
        self.wDialog = WriteToScriptDialog(self.Param_Dict, PlotWindow=False)

    def openLoggingOptionsDialog(self):
        self.lDialog = LoggingOptionsDialog(self.Misc_Dict, self)

    def openConfigDialog(self):
        self.configDialog = ConfigDialog(self.Param_Dict, self.Misc_Dict, self)

    def openRecalcDialog(self, axis):
        self.recalcDialog = RecalcDialog(self.Param_Dict, axis, self)
        
    def openPlotAllDialog(self):
        """Handles the plotting for several files in a series at once."""
        if not self.Param_Dict["isValidSeries"]:
            GUILogger.error("Evaluation stopped. Please open valid directory "
                            "first and enter valid series name.")
            return
        self.CheckBox_Dict["TimeSeriesProf"].setChecked(False)
        self.plotAllDialog = PlotAllDialog(self.Param_Dict)
        self.plotAllDialog.accepted.connect(lambda: self.evaluateMultiple(self.plotAllDialog.Request_Dict))

    def testWindow(self):
        """Outdated method for testing"""
        self.testWindow = ProgressDialog(self.Param_Dict, self, mode="Test")
        self.testWindow.finished.connect(self.giveFeedback)

    # %% Methods for line drawing functionality:
    def startLine(self):
        """Initiates LineDrawing in Canvas"""
        # Enables the information receival from plot
        GUILogger.info("Ready to draw a line on the plot.")
        GUILogger.log(29, "Just <b>press and release left click</b> on top of the plot.")
        toolbar = self.Param_Dict["CurrentPlotWindow"].toolbar
        toolbar._active = "ZOOM"  # This will set the cross
        toolbar._actions["pan"].setChecked(False)
        toolbar._actions["zoom"].setChecked(False)
        if toolbar._idPress is not None:
            toolbar._idPress = toolbar.canvas.mpl_disconnect(toolbar._idPress)
        if toolbar._idRelease is not None:
            toolbar._idRelease = toolbar.canvas.mpl_disconnect(toolbar._idRelease)
        toolbar.mode = ''
        self.Edit_Dict["LineUnit"].setText(self.Param_Dict["oldGridUnit"])
        self.Starter = self.Param_Dict["CurrentPlotWindow"].canvas.mpl_connect('button_press_event', self.lStartInput)
        self.Ender = self.Param_Dict["CurrentPlotWindow"].canvas.mpl_connect('button_release_event', self.lEndInput)

    def lStartInput(self, event):
        """Handles the mouseButtonPresses"""
        sut.getCoordInput(self.Param_Dict, event, "start")
        self.cid = self.Param_Dict["CurrentPlotWindow"].canvas.mpl_connect('motion_notify_event', self.lScreenInput)
        self.Param_Dict["CurrentPlotWindow"].canvas.mpl_disconnect(self.Starter)

    def lScreenInput(self, event):
        """Updates the line on screen in real time"""
        # This line checks wheather the mouse is still over the relevant Axes
        if str(event.inaxes)[:11] == "AxesSubplot":
            xminmax = [self.Param_Dict["XLStart"], event.xdata]
            yminmax = [self.Param_Dict["YLStart"], event.ydata]
            self.Param_Dict["CurrentPlotWindow"].drawLine(xminmax, yminmax)

    def lEndInput(self, event):
        """Handles the mouseButtonReleases and passes them to simul_utils"""
        sut.getCoordInput(self.Param_Dict, event, "end")
        self.Param_Dict["CurrentPlotWindow"].canvas.mpl_disconnect(self.cid)
        sut.shuffleCoords(self.Param_Dict)
        sut.changeToLinePlot(self.Param_Dict, self.Edit_Dict)
        self.RadioDict_Dict["1DOptions"]["Line"].setChecked(True)
        self.RadioDict_Dict["DimMode"]["1D"].setChecked(True)
        self.ComboBox_Dict["YAxis"].setCurrentText(self.Param_Dict["ZAxis"])
        self.Edit_Dict["YUnit"].setText(self.Param_Dict["ZUnit"])
        self.Edit_Dict["YMin"].setText(f"{self.Param_Dict['ZMin']:.3g}")
        self.Edit_Dict["YMax"].setText(f"{self.Param_Dict['ZMax']:.3g}")
        self.CheckBox_Dict["YLog"].setChecked(self.Param_Dict["ZLog"])
        self.Param_Dict["YLog"] = self.Param_Dict["ZLog"]
        self.Param_Dict["CurrentPlotWindow"].canvas.mpl_disconnect(self.Ender)
        GUILogger.log(29, "Line inputs have been updated. Press 'Create Plot' to make the line plot.")
        toolbar = self.Param_Dict["CurrentPlotWindow"].toolbar
        toolbar._active = None

    # %% Other methods, sorted in alphabetical order:
    def closeEvent(self, event):
        """To be sure that all HelpWindows are closed and PlotWindows can't
        restore the settings anymore"""
        config = ConfigParser()
        config.read("simgui_registry/GUIconfig.ini")
        if config.getboolean("CheckBoxes", "quitdialog"):
            reply = QW.QMessageBox.question(self, "Quit GUFY?",
                                            "Do you really want to quit?\n\n"
                                            "(You may turn this off in the\n"
                                            "configuration options [Ctrl+I])",
                                            QW.QMessageBox.Yes,
                                            QW.QMessageBox.No)
            if reply == QW.QMessageBox.No:
                event.ignore()
                return
        app = QW.QApplication.instance()
        for widget in app.topLevelWidgets():
            cond1 = isinstance(widget, LoggingOptionsDialog)
            cond2 = isinstance(widget, shel.HelpWindow)
            cond3 = isinstance(widget, ConfigDialog)
            if any([cond1, cond2, cond3]):
                widget.close()
            if isinstance(widget, PlotWindow):
                widget.setParent(None)  # This is important
                widget.restoreSettings.setDisabled(True)
        super().closeEvent(event)

    def loadTestFile(self, geometry):
        """For a quick way to test, load given file."""
        if self.Param_Dict["EvalMode"] == "Series":
            self.Status_Dict["Status"].setText("Can't load in time series mode")
            return
        if geometry == 'Cartesian':
            filename = "C:/Users/Fabian Balzer/Documents/Studium/Bachelor/DataSeries/FIS_1_M=2_10_MJ_hdf5_chk_0037"
        else:
            filename = "C:/Users/Fabian Balzer/Documents/Studium/Bachelor/DataSeries/SI_2D_hdf5_chk_0000"
        self.Param_Dict["SingleDataSet"] = self.loadFile(filename)
        self.Param_Dict["CurrentDataSet"] = self.Param_Dict["SingleDataSet"]
        self.Param_Dict["Seriesname"] = ""
        self.Status_Dict["Series"].setText(self.Param_Dict["Seriesname"])
        self.Param_Dict["Filename"] = filename
        self.Param_Dict["isValidFile"], self.Param_Dict["isValidSeries"] = True, False
        self.Status_Dict["Status"].setText(geometry + " test file loaded.")
        self.setUpFile(geometry)

    def loadTestSeries(self):
        """For a quick way to test, load a given series."""
        if self.Param_Dict["EvalMode"] == "Single":
            self.RadioDict_Dict["EvalMode"]["Time series"].setChecked(True)
        seriesname = "C:/Users/Fabian Balzer/Documents/Studium/Bachelor/DataSeries/SI_2D_hdf5_chk_000?"
        self.Param_Dict["Seriesname"] = "SI_2D_hdf5_chk_000?"
        self.Status_Dict["Series"].setText('Series:' + self.Param_Dict["Seriesname"])
        self.Status_Dict["Status"].setText("Loading series '{}'...".format(self.Param_Dict["Seriesname"]))
        self.Status_Dict["Status"].repaint()
        ts = yt.load(seriesname)
        dsList = [yt.load(filename) for filename in ts._pre_outputs]
        self.Param_Dict["DataSeries"] = dsList
        self.Param_Dict["Filename"] = ""
        self.Param_Dict["Directory"] = seriesname.strip("/SI_2D_hdf5_chk_000?")
        self.Status_Dict["File"].setText(self.Param_Dict["Filename"])
        self.Param_Dict["isValidFile"], self.Param_Dict["isValidSeries"] = True, True
        self.Status_Dict["Status"].setText("Test time series loaded.")
        self.setUpSeries()


def startProgram():
    """A function to include everything needed to start the application"""
    sut.checkVersions()  # Check if sufficient modules are installed
    # Check whether there is already a running QApplication (e.g. if running
    # from an IDE). This setup prevents crashes for the next run:
    qapp = QW.QApplication.instance()
    if not qapp:
        qapp = QW.QApplication(sys.argv)
    app = GUFYMainWindow()  # creating the instance
    app.show()
    qapp.exec_()  # Start the Qt event loop


if __name__ == "__main__":  # run if the program is properly started by
    startProgram()  # running GUFY.py.
