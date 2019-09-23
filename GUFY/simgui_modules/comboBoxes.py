# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the combo boxes
"""
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
import yt
import simgui_modules.lineEdits as LE


class coolComboBox(QW.QComboBox):
    """Modified version of QComboBoxes.
    params:
        items: List of Strings to be displayed in the box
        tooltip: optionally create a tooltip for the box
    """
    def __init__(self, items, tooltip=None, width=200):
        super().__init__()
        self.addItems(items)
        self.setToolTip(tooltip)
        self.setListWidth(200)
        if width is not None:
            self.setFixedWidth(width)

    def setListWidth(self, width):
        """Set the width of the ListView to with in pixels"""
        self.setStyleSheet(f"""
        QComboBox {{background-color: qlineargradient(x1: 0, y1: 0, 
        x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); font: bold 12px;
        border: 2px solid gray; border-radius: 2px;
        padding: 1px 1px 1px 3px; height: 20px}}
        QComboBox::drop-down {{subcontrol-origin: padding; subcontrol-position:
        top right; width: 15px; border-left-width: 2px; border-left-color:
        darkgray; border-left-style: solid; border-top-right-radius: 2px;
        border-bottom-right-radius: 2px; selection-background-color: gray}}
        QComboBox:focus {{border-color: rgb(79,148,205)}}
        QComboBox:hover {{border-color: rgb(79,148,205)}}
        QComboBox QListView {{min-height: 100px;background-color: solid gray;
        border: 2px solid gray; min-width: {width}px;}}""")
        


# %% Creation
def createAllComboBoxes(Param_Dict, ComboBox_Dict):
    """Creates all necessary ComboBoxes and stores them in Box_Dict.
    params:
        Param_Dict: Parameter Dictionary
        ComboBox_Dict: ComboBox Dictionary
    """
    for axis in ["X", "Y", "Z", "N"]:
        ComboBox_Dict[axis + "Axis"] = createAxesBoxes(axis)
    ComboBox_Dict["YWeight"] = createWeightBoxes("Y")
    ComboBox_Dict["ZWeight"] = createWeightBoxes("Z")
    ComboBox_Dict["TimeQuantity"] = createTimeQuantityBox()
    # Iterating would produce weird errors.
    hand = Param_Dict["SignalHandler"]
    ComboBox_Dict["XAxis"].currentIndexChanged.connect(lambda: hand.getAxisInput("X"))
    ComboBox_Dict["YAxis"].currentIndexChanged.connect(lambda: hand.getAxisInput("Y"))
    ComboBox_Dict["ZAxis"].currentIndexChanged.connect(lambda: hand.getAxisInput("Z"))
    ComboBox_Dict["NAxis"].currentIndexChanged.connect(lambda: hand.getAxisInput("N"))
    ComboBox_Dict["YWeight"].currentIndexChanged.connect(lambda: hand.getWeightField("Y"))
    ComboBox_Dict["ZWeight"].currentIndexChanged.connect(lambda: hand.getWeightField("Z"))
    ComboBox_Dict["TimeQuantity"].currentIndexChanged.connect(lambda: hand.getTimeQuantityInput())


def createAxesBoxes(axis, width=150):
    """Create ComboBoxes with set width for each Axis.
    params:
        axis: "X", "Y" and "Z" for the corresponding field
        width: width of the boxes
    returns:
        comboBox
    """
    # Initialize ComboBoxes for first and second axes:
    tooltip = "Select field to be plotted for " + axis + "-Axis"
    if axis == "X":
        comboBox = coolComboBox(['x', 'y', 'z'], tooltip, width)
    elif axis == "Y":
        comboBox = coolComboBox(['dens', 'temp'], tooltip, width)
        comboBox.setCurrentText('temp')
    # Initialize ComboBox for selecting 3rd dimension:
    elif axis == "Z":
        tooltip = "Select field to be displayed by color scheme"
        comboBox = coolComboBox(['dens', 'temp'], tooltip, width)
    # Initialize ComboBox for selecting slice normal axis
    elif axis == "N":
        tooltip = 'Toggle normal axis for slices or projection'
        comboBox = coolComboBox(['x', 'y', 'z'], tooltip, width)
        comboBox.setCurrentText('x')
    return comboBox


def createWeightBoxes(axis, width=150):
    """Create ComboBoxes with set width for the weight fields necessary for
    profile and phase plots.
    params:
        axis: "Y" and "Z" for the corresponding field
        width: width of the boxes
    returns:
        comboBox
    """
    # Initialize ComboBoxes for first and second axes:
    tooltip = "Select weight field to be used for " + axis + "-Axis"
    comboBox = coolComboBox(['None', 'cell_mass', 'dens', 'temp'], tooltip, width)
    return comboBox


def createTimeQuantityBox(width=150):
    """Create a comboBox to hold the quantity that is to be calculated for each
    dataset whenever time is used as x-axis for profile plots.
    I got the ideas for quantitis
    from https://yt-project.org/doc/analyzing/objects.html"""
    tooltip = "Select which quantity of the field is calculated for each dataset"
    comboBox = coolComboBox(["max", "min", "weighted_average",
                             "weighted_variance", "sum"], tooltip, width)
    comboBox.setListWidth(150)
    return comboBox
