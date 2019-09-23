# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the buttons
"""


import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
from simgui_modules.helpWindows import HelpWindow


class coolButton(QW.QPushButton):
    def __init__(self, width=None, text="", tooltip="", enabled=True):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setEnabled(enabled)
        if width is not None:
            self.setFixedWidth(width)
        self.setButtonStyle()

    def setButtonStyle(self,  backStart="#f6f7fa", backStop="#dadbde",
                       borderColor="100, 100, 100", bold="", height=20):
        """Sets the background and border color of the button and turns its
        text bold if requested."""
        self.setStyleSheet(
f"""QPushButton {{height: {height}px; background-color: 
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {backStart}, stop: 1 {backStop});
border-style: outset; border-width: 2px; border-radius: 5px; 
border-color: rgb({borderColor}); font: {bold} 14px; padding: 6px}}
QPushButton:hover {{background-color:
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
0 rgb(240, 240, 255), stop: 1 rgb(200, 200, 200))}}
QPushButton:pressed {{background-color:
qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:
0 rgb(200, 200, 200), stop: 1 rgb(140, 140, 140))}}""")

    def makeTextBold(self, height=20):
        self.setButtonStyle(bold="bold", height=height)

    def makeButtonRed(self):
        self.setButtonStyle(borderColor="255, 0, 0", bold="bold")


class HelpButton(coolButton):
    """A button that can be used to call a help window"""
    def __init__(self):
        super().__init__(width=None, text="", tooltip="Open help for current "
                         "plot mode", enabled=True)
        self.makeTextBold(height=12)
        self.clicked.connect(lambda: print("This is a dummy connection"))
        icon = QG.QIcon("simgui_registry/Icons/questionmark.png")
        self.setIcon(icon)

    def setToHelp(self, key):
        """Connects the button to the help function dialog supplied by key"""
        self.clicked.disconnect()
        self.clicked.connect(lambda: self.openHelpWindow(key))

    def openHelpWindow(self, key):
        """Opens a help window"""
        self.helpWindow = HelpWindow(key, parent=self.parent().parent().parent().parent())
        self.helpWindow.show()


# %% Buttons
def createAllButtons(Button_Dict):
    """Creates all necessary Buttons and stores them in Button_Dict.
    params:
        Button_Dict: Button Dictionary
    """
    Button_Dict["Open"] = createOpenButton()
    Button_Dict["Evaluate"] = createEvalButton()
    Button_Dict["PlotAll"] = createPlotAllButton()
    Button_Dict["QuickCart"] = createQuickFileButton("cartesian")
    Button_Dict["QuickCyli"] = createQuickFileButton("cylindrical")
    Button_Dict["QuickSeries"] = coolButton(text="Load a time series")
    Button_Dict["PlotHelp1D"] = HelpButton()
    Button_Dict["PlotHelp2D"] = HelpButton()
    Button_Dict["AddDerField"] = coolButton(text="Add new derived field",
                                            tooltip=("Click to open a dialog "
                                            "for adding a derived field"))
    Button_Dict["WriteScript"] = coolButton(text="Write settings to script", tooltip="Click to "
                                            "open a dialog for writing the "
                                            "current settings to a reproduci"
                                            "ble script")
    Button_Dict["MakeLinePlot"] = createLinePlotButton()
    for axis in ["X", "Y", "Z"]:
        Button_Dict[axis + "Calc"] = extremaButton()
        Button_Dict[axis + "Recalc"] = extremaButton(width=None)
    Button_Dict["PrintDict"] = coolButton(text="Print parameter dictionary")


def createOpenButton():
    """Initialize Button for opening file or directory.
    Text and tooltip are added in changeOpenButton method."""
    button = coolButton()
    button.makeTextBold()
    return button


def createEvalButton():
    """Create QButton to start evaluation"""
    button = coolButton(text="Create Plot")
    button.setToolTip("Start evaluation of data with current parameters [Ctrl+Return]")
    button.makeTextBold()
    return button


def createPlotAllButton():
    """Create QButton to start the evaluation of all files"""
    button = coolButton(text="Create Plot for each file")
    button.setToolTip("Evaluate each file with the current parameters")
    button.makeTextBold()
    button.setHidden(True)
    return button


def createQuickFileButton(geometry):
    """Create QButton to quickly open File"""
    button = coolButton(text=("Load " + geometry + " file"))
    return button


def createLinePlotButton():
    """Create QButton to start linePlotting"""
    button = coolButton(width=150)
    button.setText("Get Points for LinePlot")
    button.setToolTip("Starts a mode where you can draw a line")
    button.hide()
    return button


class extremaButton(coolButton):
    """We need our Button to have a method where we can easily connect and dis-
    connect it to calculating or setting the extrema."""
    def __init__(self, width=150):
        super().__init__(width=width)
        self.hide()
        self.clicked.connect(lambda: print("This is just a placeholder so we "
                                           "can disconnect later :)"))

    def setToCalculate(self, Param_Dict, axis):
        self.setText("Calculate Extrema")
        self.setToolTip("Check the dataset to calculate minimum and maximum "
                        "values of this field")
        self.clicked.disconnect()
        self.clicked.connect(lambda: Param_Dict["SignalHandler"].calculateExtrema(axis))

    def setToSetExtrema(self, Param_Dict, axis):
        self.setText("Set Extrema")
        self.setToolTip("Set the minimum and maximum to the extrema of this field")
        self.clicked.disconnect()
        self.clicked.connect(lambda: Param_Dict["SignalHandler"].setExtrema(axis))

    def setToRecalculate(self, axis, Window):
        self.setIcon(QG.QIcon("simgui_registry/Icons/Recalculate.png"))
        self.setToolTip("Calculate the global extrema for this field or recalc"
                        "ulate them for the current dataset")
        self.clicked.disconnect()
        self.clicked.connect(lambda: Window.openRecalcDialog(axis))
        
