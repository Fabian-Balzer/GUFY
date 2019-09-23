# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

This module is for the PlotWindow class (a Dialog that can both be stand-alone
and embedded).

The module is structured as follows:
    - The coolToolbar class for the NavigationToolbar
    - The PlotWindow class for hosting canvas, Buttons and Toolbar
"""
from copy import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
from simgui_modules.buttons import coolButton
from simgui_modules.logging import GUILogger
from simgui_modules.scriptWriter import WriteToScriptDialog
from simgui_modules.plots import setProfileAxisSettings
from simgui_modules.utils import convertToLessThanThree, emitStatus, mean, \
    drawTimestampBox, annotateStartEnd


matplotlib.rcParams.update({"figure.figsize": (10, 8),
                            "figure.autolayout": True, "axes.labelsize": 16,
                            "axes.titlesize": 16, "font.size": 16,
                            "legend.fontsize": 14, "xtick.labelsize": 14,
                            "ytick.labelsize": 14, "axes.linewidth": 2,
                            "xtick.major.size": 8, "xtick.major.width": 1,
                            "xtick.minor.size": 4, "xtick.minor.width": 1,
                            "ytick.major.size": 8, "ytick.major.width": 1,
                            "ytick.minor.size": 4, "ytick.minor.width": 1})


# %% The coolToolbar class for the NavigationToolbar
class coolToolbar(NavigationToolbar):
    """Modified matplotlib NavigationToolbar for GUFY, connected to a Label
    where information about the dataset and the current cursor position can be
    displayed"""
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.setOrientation(QC.Qt.Vertical)
        self.setFixedWidth(50)
        self.parent = parent
        self.fileInfo = ""
        self._actions["configure_subplots"].deleteLater()
#        self._actions["configure_subplots"].setDisabled(True)
#        self._actions["back"].deleteLater()  # this caused some problems
#        self._actions["forward"].deleteLater()
        self.locLabel.hide()
        self.setEnabled(False)

    def set_message(self, s):
        """This message is shown below the canvas. It should display
        information about the file unless the user hovers over the plot."""
        self.message.emit(s)
        if s == "":
            self.parent.infoLabel.setText(self.fileInfo)
        else:
            self.parent.infoLabel.setText(s)


# %% The PlotWindow class for hosting canvas, Buttons and Toolbar
class PlotWindow(QW.QDialog):
    """A Widget that can optionally be opened as an external window. Includes
    the options to restore the settings used for the plot, navigation on the
    plot, and possible write-out to a script.
    I apologize that this class is so unorganized.
    Parameters:
        Status_Dict: If embedded, it can be connected to the MainWindow Status
        parent: usually the MainWindow
    """
    def __init__(self, Status_Dict=None, parent=None):
        super().__init__(parent)
        self.move(20, 20)
        self.setMinimumSize(400, 300)
        self.setWindowFlags(  # Set minimize, maximize and close button
                            QC.Qt.Window |
                            QC.Qt.CustomizeWindowHint |
                            QC.Qt.WindowTitleHint |
                            QC.Qt.WindowMinimizeButtonHint |
                            QC.Qt.WindowMaximizeButtonHint |
                            QC.Qt.WindowCloseButtonHint)
        # a figure instance to plot on
        self.figure = plt.figure(tight_layout=True)

        canvasWidget = QW.QGroupBox()
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        canvasLayout = QW.QVBoxLayout(canvasWidget)
        canvasLayout.setContentsMargins(0, 0, 0, 0)
        canvasLayout.addWidget(self.canvas)
        canvasWidget.setStyleSheet(
"""QGroupBox {border-style: outset; border-width: 2px; border-radius: 2px; 
border-color: rgb(0, 0, 0)}""")

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = coolToolbar(self.canvas, self)

        self.writeFileButton = coolButton(width=None, text="Write plot to script")
        self.writeFileButton.setToolTip("Write the plot with its current set"
                                        "tings to a script to reproduce it la"
                                        "ter")
        self.restoreSettings = coolButton(width=None, text="Restore plot settings")
        self.restoreSettings.setToolTip("Restore the GUI setting to a state "
                                        "they were in when the plot was created")
        self.externalWindowButton = coolButton(width=None, text="Open this plot "
                                               "in a separate window")
        self.externalWindowButton.setToolTip("Opens another window, containing"
                                             " the same plot")
        self.writeFileButton.clicked.connect(self.savefile)
        self.restoreSettings.clicked.connect(self.restoreFromParam_Dict)
        self.externalWindowButton.clicked.connect(self.openInExternalWindow)
        self.writeFileButton.setDisabled(True)
        self.restoreSettings.setDisabled(True)
        self.externalWindowButton.setDisabled(True)
        self.infoLabel = QW.QLabel("")
        self.infoLabel.setFixedHeight(15)
#        self.infoLabel.hide()  # This causes the plot to reach different sizes
        scriptWriterWid = QW.QWidget()
        scriptWriterWid.setFixedHeight(40)
        scriptWriterLayout = QW.QHBoxLayout(scriptWriterWid)
        scriptWriterLayout.setContentsMargins(0, 0, 0, 0)
        scriptWriterLayout.addWidget(self.restoreSettings)
        scriptWriterLayout.addWidget(self.externalWindowButton)
        scriptWriterLayout.addWidget(self.writeFileButton)
        # set the layout
        vWid = QW.QWidget()
        vlayout = QW.QVBoxLayout(vWid)
        vlayout.setContentsMargins(1, 0, 1, 0)
        vlayout.addWidget(canvasWidget)
        vlayout.addWidget(self.infoLabel)
        vlayout.addWidget(scriptWriterWid)
        vlayout.setSpacing(1)
        vlayout.setStretch(0, 1)
        vlayout.setStretch(1, 10)
        hwid = QW.QGroupBox("Plot window")
        hlayout = QW.QHBoxLayout(hwid)
        hlayout.addWidget(self.toolbar)
        hlayout.addWidget(vWid)
        hlayout.setStretch(1, 1)
        hlayout.setContentsMargins(3, 3, 3, 3)
        layout = QW.QVBoxLayout()
        layout.addWidget(hwid)
        layout.setContentsMargins(1, 0, 1, 0)
        self.setLayout(layout)

        self.hasProfile = False  # We want to keep track if there is a single profile plot on the plotwindow
        if Status_Dict is not None:
            # Give access to main window status bar if plot is on there:
            self.Status_Dict = Status_Dict
            self.isExternalWindow = False
        else:
            self.isExternalWindow = True
            self.Status_Dict = {}
            self.Status_Dict["Status"] = QW.QLabel("External Window of the plot")
            self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
            bar = QW.QStatusBar()
            bar.addPermanentWidget(self.Status_Dict["Status"])
            bar.setFixedHeight(25)
            layout.addWidget(bar)

    def startPlot(self, plot, Param_Dict, worker=None):
        """Get the figure ready for plotting.
        Parameters:
            plot: yt plot object
            Param_Dict: Parameter Dictionary for dimensions and fields
        """
        emitStatus(worker, "Starting the plot")
        self.plot = plot
        self.prepareFigure()
        if Param_Dict["DimMode"] == "2D":
            divider = make_axes_locatable(self.ax)
            self.cax = divider.append_axes("right", size="5%", pad=0.05)
            self.makePlot(plot, Param_Dict, 3, worker)
        else:
            self.makePlot(plot, Param_Dict, 2, worker)

    def prepareFigure(self):
        """Clears the figure and prepares the ax."""
        self.figure.clear()
        self.hasProfile = False
        # create an axis
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.1, bottom=0.1, right=0.8, top=0.9,
                                    wspace=None, hspace=None)

    def makeProfilePlot(self, Param_Dict, arr, labels, worker=None):
        """Plots the data of the array to the axes."""
        self.arr = arr
        self.labels = labels
        emitStatus(worker, "Starting the plot")
        if Param_Dict["AddProfile"]:
            self.ax.tick_params(axis='y',)
            self.twinax = self.ax.twinx()
            x_values = arr[0].to_value(Param_Dict["XUnit"])
            for i in range(len(arr)-1):
                y_values = arr[i+1].to_value(Param_Dict["YUnit"])
                label = labels[i]
                self.twinax.plot(x_values, y_values, ":", linewidth=3,
                                 label=label)
            emitStatus(worker, "Setting plot modifications")
            setProfileAxisSettings(Param_Dict, "Y", self.twinax)
            self.twinax.tick_params(axis='y')
            # ask matplotlib for the plotted objects and their labels
            lines, labels = self.ax.get_legend_handles_labels()
            lines2, labels2 = self.twinax.get_legend_handles_labels()
            self.ax.legend(lines + lines2, labels + labels2)
            self.hasProfile = False  # We only want the user to be able to add a plot if there is only one profile
            Param_Dict["SignalHandler"].changeToProfile()
        else:
            self.prepareFigure()  # Clear everything before plotting
            # get x- and y-values and plot them:
            x_values = arr[0].to_value(Param_Dict["XUnit"])
            for i in range(len(arr)-1):
                y_values = arr[i+1].to_value(Param_Dict["YUnit"])
                label = labels[i]
                self.ax.plot(x_values, y_values, "-", linewidth=3, label=label)
            emitStatus(worker, "Setting plot modifications")
            setProfileAxisSettings(Param_Dict, "Y", self.ax)
            self.hasProfile = True
            Param_Dict["SignalHandler"].changeToProfile()
            if Param_Dict["Timestamp"] and Param_Dict["XAxis"] != "time":
                if len(arr) > 2:  # This can probably be done more elegantly
                    GUILogger.warning("Timestamp is not annotated for multiple"
                                      " profiles. Sorry for leaving the CheckBox there.")
                else:
                    drawTimestampBox(Param_Dict, self.ax)
            self.ax.legend()
            self.ax.grid()
        setProfileAxisSettings(Param_Dict, "X", self.ax)
        self.ax.set_title(r"{}".format(Param_Dict["PlotTitle"]))
        emitStatus(worker, "Drawing plot onto the canvas")
        self.canvas.draw()  # called twice because somehow it isn't fully sized
        self.canvas.draw()  # at first... I don't know why.
        self.copyParamDict(Param_Dict)

    def makePlot(self, plot, Param_Dict, dim, worker=None):
        """Plot the given plot onto the figure. (Except for profiles)
        Parameters:
            plot: yt plot object
            Param_Dict: Parameter Dictionary containing the field to be plotted
            dim: dimensionality of the plot
        """
        mode = Param_Dict["PlotMode"]
        # We need to pass our axes to yt so it can setup the plots
        if mode == "Line":
            field = Param_Dict["YAxis"]
            plot.plots[field].axes = self.ax
        else:
            field = Param_Dict["ZAxis"]
            if Param_Dict["DomainDiv"]:
                field = "Normed " + field
            plot.plots[field].axes = self.ax
        if dim == 3:
            plot.plots[field].cax = self.cax
        emitStatus(worker, "Drawing plot onto the canvas")
        plot._plot_valid = False  # to make _setup_plots() works
        plot._setup_plots()
        if mode == "Line":
            self.ax.set_ylim(Param_Dict["YMin"], Param_Dict["YMax"])
            annotateStartEnd(Param_Dict, self.ax)
        if mode in ["Slice", "Projection"]:
            if Param_Dict["SetAspect"]:
                self.ax.set_aspect("auto")
            else:
                self.ax.set_aspect("equal")
        if mode in ["Line", "Phase"]:
            if Param_Dict["Timestamp"]:
                drawTimestampBox(Param_Dict, self.ax)
        # refresh canvas:
        self.canvas.draw()  # called twice because somehow it isn't fully sized
        self.canvas.draw()  # at first... I don't know why.
        self.copyParamDict(Param_Dict)

    def copyParamDict(self, Param_Dict):
        """Stores a copy of the parameter dictionary as an attribute, displays
        dataset information and enables the buttons"""
        Param_Dict["isValidPlot"] = Param_Dict["PlotMode"]
        # Save a copy of the parameter dictionary so it is reproducible
        self.Param_Dict = copy(Param_Dict)
        # We need a reference to the original signal handler to stick around
        self.Param_Dict["SignalHandler"] = Param_Dict["SignalHandler"]
        if not self.isExternalWindow:
            self.Param_Dict["CurrentPlotWindow"] = self
        ds = str(Param_Dict["CurrentDataSet"])
        mode = Param_Dict["PlotMode"]
        if mode in ["Profile", "Line"]:
            field = Param_Dict["YAxis"]
        else:
            field = Param_Dict["ZAxis"]
        if Param_Dict["EvalMode"] == "Single":
            time = Param_Dict["DataSetTime"]
        else:
            time = Param_Dict["DataSetDict"][ds + "Time"]
        timeString = "{:.3g} ".format(time.value)
        timeString += str(time.units)
        info = f"{ds}: {mode} plot of {field} at {timeString}"
        if self.Param_Dict["XAxis"] == "time":
            series = Param_Dict["Seriesname"]
            quan = Param_Dict["TimeQuantity"]
            info = f"{series}: Profile plot of the {quan} of {field}"
        self.toolbar.fileInfo = info
        self.toolbar.setEnabled(True)
        self.infoLabel.setText(info)
        self.restoreSettings.setEnabled(True)
        self.writeFileButton.setEnabled(True)
        if not self.isExternalWindow:
            self.externalWindowButton.setEnabled(True)

    def restoreFromParam_Dict(self):
        """Restores the settings used for the plot to the GUI"""
        self.readOutExtrema()
        self.Param_Dict["SignalHandler"].restoreFromParam_Dict(self.Param_Dict)
        GUILogger.info("The settings to recreate this plot have been "
                       "transferred to the GUI.")

    def readOutExtrema(self):
        """Reads out the current constraints of x- and y-axis and stores them
        before restoring them to the gui"""
        mode = self.Param_Dict["PlotMode"]
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        if mode in ["Profile", "Phase"]:
            self.Param_Dict["XMin"] = xmin
            self.Param_Dict["XMax"] = xmax
        if mode in ["Profile", "Phase", "Line"]:
            self.Param_Dict["YMin"] = ymin
            self.Param_Dict["YMax"] = ymax
        if mode in ["Slice", "Projection"]:
            self.Param_Dict["HorWidth"] = abs(xmin-xmax)
            self.Param_Dict["VerWidth"] = abs(ymin-ymax)
            self.Param_Dict["Zoom"] = 1.0
            aligned = self.Param_Dict["NormVecMode"] == "Axis-Aligned"
            cart = self.Param_Dict["Geometry"] == "cartesian"
            if cart or self.Param_Dict["NAxis"] == "theta" and aligned:
                horCen = mean([xmin, xmax])
                verCen = mean([ymin, ymax])
                if self.Param_Dict["NAxis"] == "theta":
                    n = 2
                else:
                    n = ["x", "y", "z"].index(self.Param_Dict["NAxis"])
                horAxis = ["X", "Y", "Z"][convertToLessThanThree(n+1)]
                verAxis = ["X", "Y", "Z"][convertToLessThanThree(n+2)]
                self.Param_Dict[horAxis + "Center"] = horCen
                self.Param_Dict[verAxis + "Center"] = verCen
            elif not aligned:
                GUILogger.warning("For off-axis plots, setting the center "
                                  "coordinates is not supported.")
            else:
                GUILogger.warning("Reading out the center coordinates is not "
                                  "supported for having "
                                  f"{self.Param_Dict['NAxis']} as normal axis."
                                  "This may produce weird behaviour.")

    def saveFigure(self, saveName):
        self.figure.savefig(saveName)

    def drawLine(self, x0x1, y0y1):
        """Draws a line from a given start point to a given end point in real
        time.
        Parameters:
            x0x1: boundaries for x
            y0y1: boundaries for y
        """
        # remove all existing lines first
        for line in self.ax.get_lines():
            line.remove()
        # create a new line with (x0, x1, y0, y1)
        self.line = mlines.Line2D(x0x1, y0y1)
        self.line.set_color('black')
        # Add it to the plot
        self.ax.add_line(self.line)
        self.canvas.draw()

    def savefile(self):
        """Opens a dialog to save the plot as a script"""
        self.readOutExtrema()
        self.writeDialog = WriteToScriptDialog(self.Param_Dict)

    def openInExternalWindow(self):
        """Open another PlotWindow containing the same plot"""
        self.readOutExtrema()
        self.externalWindow = PlotWindow()
        if self.Param_Dict["PlotMode"] == "Profile":
            self.externalWindow.makeProfilePlot(self.Param_Dict, self.arr,
                                                self.labels)
        else:
            self.externalWindow.startPlot(self.plot, self.Param_Dict)
        self.externalWindow.setWindowTitle(f"External {self.Param_Dict['PlotMode']}"
                                           f"plot PlotWindow of "
                                           f"{self.Param_Dict['CurrentDataSet']}")
        self.externalWindow.show()
