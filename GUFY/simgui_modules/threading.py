# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

A module for the progress bar updates and threading, including the heads of the
evaluation functions.

The module is structured as follows:
    - The ProgressDialog class for creating a progress window when plotting
    - The Worker classes for carrying out the plotting process
    - Function for evaluating single file data
    - Function for evaluating time series data
"""
import numpy as np
import traceback
import PyQt5.QtWidgets as QW
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import simgui_modules.plots as splot  # used in eval-commands
import simgui_modules.utils as sut
from simgui_modules.additionalWidgets import GUILogger


# %% The ProgressDialog class for creating a progress window when plotting
class ProgressDialog(QW.QDialog):
    """A dialog that pops up when a plot is being made. Shows a progressbar
    and a status concerning plotting, and contains a button to stop the plot
    process. Automatically closes upon finishing.
    Parameters:
        Param_Dict: For the plot parameters.
        parent: QObject: preferably the main window.
        all_: bool: unimplemented function to plot everything
    """
    finished = QC.pyqtSignal(bool)  # signal to indicate success
    def __init__(self, Param_Dict, parent, mode, Request_Dict=None, slider=None):
        super().__init__(parent=parent)
        self.setModal(True)
        self.setWindowFlags(  # This will stop the close button from appearing
                            QC.Qt.Window |
                            QC.Qt.CustomizeWindowHint |
                            QC.Qt.WindowTitleHint |
                            QC.Qt.WindowMinimizeButtonHint |
                            QC.Qt.WindowStaysOnTopHint
                            )
        self.Request_Dict = Request_Dict
        self.mode = mode
        self.initUi()
        self.determineProgressLength(Param_Dict)
        self.setWindowTitle("Plotting in progress...")
        if mode == "Test":
            self.parent().progressWorker = TestPlotWorker()
        elif mode == "PlotSingle":
            self.parent().progressWorker = PlotSingleWorker(Param_Dict)  # Create worker for plotting
        elif mode == "PlotAll":
            self.parent().progressWorker = PlotMultipleWorker(Param_Dict,
                                                              Request_Dict,
                                                              slider)
        else:
            self.parent().progressWorker = TestPlotWorker()
        self.parent().thread = QC.QThread()  # Create thread for worker. For safety reasons leave a reference on the main window.
        self.signalsConnection()
        self.parent().progressWorker.moveToThread(self.parent().thread)
        self.parent().thread.start()  # Start the thread
        self.resize(400, self.height())
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.show()

    def initUi(self):
        """Initiates the visual elements, including a progress bar and a cancel
        button"""
        self.progressBar = QW.QProgressBar()
        self.infoLabel = QW.QLabel()
        self.cancelButton = QW.QPushButton("Cancel")
        buttonBox = QW.QWidget()
        buttonBoxLayout = QW.QHBoxLayout(buttonBox)
        buttonBoxLayout.addStretch(1)
        buttonBoxLayout.addWidget(self.cancelButton)
        buttonBoxLayout.setContentsMargins(0, 0, 0, 0)
        layout = QW.QVBoxLayout(self)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.infoLabel)
        if self.mode == "PlotAll":
            self.multipleProgressBar = QW.QProgressBar()
            self.multipleProgressBar.setRange(0, self.Request_Dict["PlotNumber"])
            self.multipleProgressBar.setValue(0)
            layout.addWidget(self.multipleProgressBar)
            self.multiInfoLabel = QW.QLabel(f"Currently working on plot 1/{self.Request_Dict['PlotNumber']}...")
            layout.addWidget(self.multiInfoLabel)
        layout.addStretch(1)
        layout.addWidget(buttonBox)

    def determineProgressLength(self, Param_Dict):
        """Calculate the number of checkpoint steps for the current plot
        settings and format the slider accordingly."""
        self.progressBar.setRange(0, 0)
        # startplot, modifications, annotations, startplot,
        length = 6  # _setupPlots, finish
        if Param_Dict["PlotMode"] == "Profile":
            length += sut.calculateProfileAdditions(Param_Dict)
        self.progressBar.setRange(0, length)
        self.progressBar.setValue(0)

    def updateProgress(self, message):
        """Updates the progressbar by one step and sets the text of the
        infoLabel to message."""
        value = self.progressBar.value()
        self.progressBar.setValue(value + 1)
        self.infoLabel.setText(f"{message}...")

    def updateMultiProgress(self):
        oldValue = self.multipleProgressBar.value()
        self.multipleProgressBar.setValue(oldValue + 1)
        self.progressBar.setValue(0)
        text = f"{oldValue+2}/{self.Request_Dict['PlotNumber']}"
        self.multiInfoLabel.setText(f"Currently working on plot {text}...")
        GUILogger.debug(text)

    def signalsConnection(self):
        """Connect the cancelButton"""
        self.parent().progressWorker.progressUpdate.connect(self.updateProgress)
        self.parent().progressWorker.finished.connect(lambda: self.close())
        if self.mode == "PlotAll":
            self.parent().progressWorker.multiProgress.connect(self.updateMultiProgress)
        self.cancelButton.clicked.connect(self.stopProcess)
        self.parent().thread.started.connect(self.parent().progressWorker.plot)

    def keyPressEvent(self, event):
        if event.key() == QC.Qt.Key_Escape:
            self.stopProcess()

    def closeEvent(self, event):
        self.parent().thread.quit()
        super().closeEvent(event)

    def stopProcess(self):
        self.infoLabel.setText(f"Plotting interrupted. Please wait until the current step is finished...")
        self.cancelButton.setDisabled(True)
        plotWindow = self.parent().Param_Dict["CurrentPlotWindow"]
        plotWindow.restoreSettings.setDisabled(True)
        plotWindow.writeFileButton.setDisabled(True)
        plotWindow.externalWindowButton.setDisabled(True)
        self.parent().progressWorker._isRunning = False


# %% The Worker classes for carrying out the plotting process
class WorkerBase(QC.QObject):
    """A base class for objects to be used during threading"""
    finished = QC.pyqtSignal(bool)
    progressUpdate = QC.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._isRunning = True
        self.oldMessage = "Starting up"


class PlotSingleWorker(WorkerBase):
    """A worker to carry out a single plot"""

    def __init__(self, Param_Dict):
        super().__init__()
        self.Param_Dict = Param_Dict

    @QC.pyqtSlot()  # This is necessary to make the threading work.
    def plot(self):
        try:
            evaluateSingle(self.Param_Dict, self)
        except sut.WorkingException as e:
            GUILogger.error(str(e.args[0]))
        except Exception as e:
            traceback.print_exc()  # This will print the complete traceback including links to the lines
            GUILogger.exception("A yt-internal exception occured:<br><b><font color"
                                f'="DarkRed">{type(e).__name__}:</font><br>'
                                f"{e}</b>")
            GUILogger.log(29, "I've printed the traceback for you.")
            self._isRunning = False
        self.finished.emit(self._isRunning)


class PlotMultipleWorker(WorkerBase):
    """A worker to carry out multiple consecutive plots"""
    finished = QC.pyqtSignal(bool, str)
    multiProgress = QC.pyqtSignal()

    def __init__(self, Param_Dict, Request_Dict, slider):
        super().__init__()
        self.Param_Dict = Param_Dict
        self.Request_Dict = Request_Dict
        self.slider = slider

    @QC.pyqtSlot()  # This is necessary to make the threading work.
    def plot(self):
        try:
            evaluateMultiple(self.Param_Dict, self.Request_Dict, self.slider, self)
        except sut.WorkingException as e:
            GUILogger.error(str(e.args[0]))
        except Exception as e:
            traceback.print_exc()  # This will print the complete traceback including links to the lines
            GUILogger.exception("A yt-internal exception occured:<br><b><font color"
                                f'="DarkRed">{type(e).__name__}:</font><br>'
                                f"{e}</b>")
            GUILogger.log(29, "I've printed the traceback for you.")
            self._isRunning = False
        self.finished.emit(self._isRunning, self.Request_Dict["Directory"])


class TestPlotWorker(WorkerBase):

    @QC.pyqtSlot()  # Override this
    def plot(self):
        import time
        for i in range(100):
            if self._isRunning:
                time.sleep(0.02)
                self.progressUpdate.emit(str(i))
        if self._isRunning:
            self.success = True
        self.finished.emit()


# %% Function for evaluating single file data
def evaluateSingle(Param_Dict, worker):
    """Handles the different cases needed for evaluation of a Data or
    DataSetSeries object.
    Parameters:
        Param_Dict: For the information to be plotted
        worker: Worker object the evaluation is initiated from
    """
    mode = Param_Dict["PlotMode"]
    sut.emitStatus(worker, f"Creating the initial {mode.lower()} plot")
    GUILogger.log(29, f"Producing the requested {mode.lower()} plot...")
    # For lineplotting we need to remember the grid unit
    Param_Dict["oldGridUnit"] = Param_Dict["GridUnit"]
    # Convenient way to choose the right function:
    eval(f"splot.{mode}Plot(Param_Dict, worker)")
    sut.emitStatus(worker, "Finishing")


# %% Function for evaluating time series data
def evaluateMultiple(Param_Dict, Request_Dict, slider, worker):
    """Evaluate the series according to the settings given from the
    plotDialog. If the makeMovie-attribute from the dialog is True, ask for a
    directory, create a folder and save the figures there."""
    mode = Param_Dict["PlotMode"]
    directory = Request_Dict["Directory"]
    onlyEvery = Request_Dict["OnlyEvery"]
    plotnum = Request_Dict["PlotNumber"]
    GUILogger.log(29, f"Producing the requested {mode.lower()} plots...")
    sut.emitStatus(worker, f"Creating the initial {mode.lower()} plot")
    # For lineplotting we need to remember the grid unit
    Param_Dict["oldGridUnit"] = Param_Dict["GridUnit"]
    i = 0
    for j in range(Request_Dict["Length"]):
        if i % onlyEvery == 0:
            # The following will set the plotWindow and dataset to the one we want
            Param_Dict["SignalHandler"].getSliderInput(value=j, seriesEval=True)
            # Convenient way to choose the right plot function
            eval(f"splot.{mode}Plot(Param_Dict, worker)")
            GUILogger.info(f"Progress: {int(i/onlyEvery+1)}/{plotnum} {mode.lower()} plots done.")
            if Request_Dict["MakeMovie"]:
                saveName = f"{directory}/{mode}plot_{i+1}"
                Param_Dict["CurrentPlotWindow"].saveFigure(saveName)
            sut.emitMultiStatus(worker, i, plotnum)
        i += 1
    slider.setValue(j)
