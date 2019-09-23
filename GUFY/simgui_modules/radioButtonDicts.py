# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the RadioButtonDicts
"""

import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW
import simgui_modules.layouts as slay
import simgui_modules.lineEdits as LE
from simgui_modules.additionalWidgets import GUILogger


class coolRadioButton(QW.QRadioButton):
    """Modified version of QRadioButtons.
    Creates a QLineEdit with a given placeholder and tooltip.
    params:
        lineText: Text to be already entered. Overrides placeholder.
        placeholder: Text to be displayed by default
        tooltip: optionally create a tooltip for the edit"""
    def __init__(self, text=None, tooltip=None, width=50):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setMinimumWidth(width)
        self.setStyleSheet("""QRadioButton {padding: 1px 1px;
                           color: black; background-color:
                           qlineargradient(x1: 0, y1: 0, 
                           2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
                           font: bold 14px} 
                           QRadioButton:checked {color: rgb(0, 0, 150)}
                           """)

    
def create_RadioButtons(group, names, tooltip=None):
    """
    Creates QRadioButtons with the names passed through 'names' and adds them
    to a RadioButton group.
    params:
        group: QButtonGroup object
        names: List of Strings for the radio button names
        tooltip: optionally create a tooltip for the buttons
    returns:
        button_dict: Dictionary of QRadioButtonObjects with their names
    """
    buttons = []
    for name in names:
        RadioButton = coolRadioButton(name, tooltip)
        group.addButton(RadioButton)
        buttons.append(RadioButton)
    button_dict = dict(zip(names, buttons))
    return button_dict


# %% Creation of the Buttons we use
def createAllRadioDicts(MainWid, Param_Dict, RadioDict_Dict):
    """Creates all necessary RadioButton Dicts and stores them in RadioDict_Dict
    params:
        MainWid: Widget where the radio groups are to be initialized
        Param_Dict: Parameter Dictionary where the values are to be stored
        RadioDict_Dict: RadioDict Dictionary
    """
    hand = Param_Dict["SignalHandler"]
    # Create a RadioGroup for Evalutation Mode to toggle between single/series.
    RadioDict_Dict["EvalMode"] = createEvalMode(MainWid)
    for button in RadioDict_Dict["EvalMode"].values():
        button.toggled.connect(lambda: hand.changeEvalMode())
    # Initialize RadioButtonGroup for projection mode (AxisAligned/Custom).
    RadioDict_Dict["NormVecMode"] = createNormVecMode(MainWid)
    for button in RadioDict_Dict["NormVecMode"].values():
        button.toggled.connect(lambda: hand.changeNormVecMode())
    RadioDict_Dict["DimMode"] = createDimMode(MainWid)
    for button in RadioDict_Dict["DimMode"].values():
        button.toggled.connect(lambda: hand.changeDimensions())
    # Create radio Groups for the user to choose plot mode.
    RadioDict_Dict["1DOptions"] = createPlotMode(0, MainWid)
    RadioDict_Dict["2DOptions"] = createPlotMode(1, MainWid)
    for button in RadioDict_Dict["1DOptions"].values():
        button.toggled.connect(lambda: hand.changeDimensions())
    for button in RadioDict_Dict["2DOptions"].values():
        button.toggled.connect(lambda: hand.changeDimensions())
    return


def createEvalMode(MainWid):
    """Initializes a radio group for toggling between the different evaluation
    modes.
    params:
        MainWid: Wid where radioGroup is initialized in
    returns:
        Dict: Dictionary of the radio buttons
    """
    # Group the buttons in a radio group
    R_G_EvalMode = QW.QButtonGroup(MainWid)
    names = ["Single file", "Time series"]
    Dict = create_RadioButtons(R_G_EvalMode, names,
                               tooltip='Set evaluation mode')
    Dict["Single file"].setChecked(True)
    return Dict


def createNormVecMode(MainWid):
    """Initializes a radio group for toggling between different modes for
    the normal axis.
    params:
        MainWid: Wid where radioGroup is initialized in
    retuns:
        wid: QWidget containing the radio buttons
        Dict: Dictionary of the radio buttons
    """
    # Slice normal axis should be optional. Create RadioGroup.
    NormVecRadioGroup = QW.QButtonGroup(MainWid)
    names = ["Axis-Aligned", "Off-Axis"]
    Dict = create_RadioButtons(NormVecRadioGroup, names,
                               tooltip='Set projection mode')
    Dict["Axis-Aligned"].setChecked(True)
    return Dict


def createDimMode(MainWid):
    """Initializes a radio group for toggling between the different plot
    modes.
    params:
        MainWid: Wid where radioGroup is initialized in
    returns:
        Dict: Dictionary of the radio buttons
    """
    Group = QW.QButtonGroup(MainWid)
    names = ["1D", "2D"]
    Dict = create_RadioButtons(Group, names, tooltip="Set dimensions of the "
                               "plot")
    Dict["2D"].setChecked(True)
    return Dict


def createPlotMode(mode, MainWid):
    """Initializes a radio group for toggling between the different plot modes.
    params:
        mode:
            0 for 1D
            1 for 2D
    returns:
        Dict: Dictionary of the radio buttons
    """
    Group = QW.QButtonGroup(MainWid)
    if mode == 0:
        names = ["Profile", "Line"]
        Dict = create_RadioButtons(Group, names, tooltip='Set plotting mode')
        Dict["Profile"].setChecked(True)
    elif mode == 1:
        names = ["Phase", "Slice", "Projection"]
        Dict = create_RadioButtons(Group, names, tooltip='Set plotting mode')
        Dict["Slice"].setChecked(True)
    return Dict
