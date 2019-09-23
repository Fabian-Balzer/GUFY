# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the line edits
"""


import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW


try:
    # Read all of the available cmaps out of a prepared txt file
    with open("simgui_registry/colormaps.txt", 'r') as cmaps:
        validColors = cmaps.read().split(", ")
except FileNotFoundError:
    validColors = ["viridis", "plasma", "inferno", "magma", "bwr", "BrBG"]
    print("colormaps.txt couln't be found")


class coolEdit(QW.QLineEdit):
    """Modified version of QLineEdits.
    Creates a QLineEdit with a given placeholder and tooltip.
    params:
        lineText: Text to be already entered. Overrides placeholder.
        placeholder: Text to be displayed by default
        tooltip: optionally create a tooltip for the edit"""
    def __init__(self, lineText=None, placeholder=None,
                 tooltip=None, width=100, parent=None):
        super().__init__(parent=parent)
        self.setPlaceholderText(placeholder)
        self.setText(lineText)
        self.setToolTip(tooltip)
        if width:
            self.setFixedWidth(width)
        self.turnTextBlack()

    def turnTextRed(self):
        """Turns the text displayed to red"""
        self.setColors("255, 0, 0", "255, 228, 225")

    def turnTextBlue(self):
        """Turns the text displayed to blue"""
        self.setColors("0, 0, 255", "240, 240, 255")

    def turnTextBlack(self):
        """Turns the text displayed to Black"""
        self.setColors("0, 0, 0", "255, 255, 255")

    def turnTextYellow(self):
        """Turns the text displayed to Black"""
        self.setColors("130, 120, 0", "255, 255, 240")

    def setColors(self, textColor, backColor):
        """Sets the text- and background color the line edit to given rgb
        triplets"""
        self.setStyleSheet(f"""QLineEdit {{border: 2px solid gray;
                           border-radius: 2px; padding: 1px 1px;
                           color: rgb({textColor}); background-color:
                           rgb({backColor}); height: 18px}}
                           QLineEdit:focus {{border-color: rgb(79,148,205)}}
                           QLineEdit:hover {{border-color: rgb(79,148,205)}}""")
        


# %% Creation and connection
def createAllEdits(Param_Dict, Edit_Dict):
    """Creates all necessary Line Edits, connects them to their slots and
    stores them in Edit_Dict.
    params:
        Param_Dict: Where the parameters entered in the edits are to be stored
        Edit_Dict: Where the LineEdits are to be stored
    """
    minmaxEdits = createExtrema()  # 6 Edits
    lineplotEdits = createStartEnd()  # 6 Edits
    unitEdits = createUnits()  # 5 Edits
    centerEdits = createCenterWidthEdits()  # 5 Edits
    normVecEdits = createNormalVectorEdits()
    for i, axis in enumerate(["X", "Y", "Z"]):
        Edit_Dict[axis + "Min"] = minmaxEdits[i]
        Edit_Dict[axis + "Max"] = minmaxEdits[i + 3]
        Edit_Dict[axis + "Unit"] = unitEdits[i]
        Edit_Dict[axis + "LStart"] = lineplotEdits[i]
        Edit_Dict[axis + "LEnd"] = lineplotEdits[i + 3]
        Edit_Dict[axis + "Center"] = centerEdits[i]
        Edit_Dict[axis + "NormDir"] = normVecEdits[i]
        Edit_Dict[axis + "NormNorth"] = normVecEdits[i+3]
    Edit_Dict["LineUnit"] = unitEdits[3]
    Edit_Dict["GridUnit"] = unitEdits[4]
    Edit_Dict["HorWidth"] = centerEdits[3]
    Edit_Dict["VerWidth"] = centerEdits[4]
    # Unfortunately iterating over the Edits and passing axis doesn't work
    hand = Param_Dict["SignalHandler"]
    Edit_Dict["XMin"].textChanged.connect(lambda: hand.getExtremaInput("X", "Min"))
    Edit_Dict["YMin"].textChanged.connect(lambda: hand.getExtremaInput("Y", "Min"))
    Edit_Dict["ZMin"].textChanged.connect(lambda: hand.getExtremaInput("Z", "Min"))
    Edit_Dict["XMax"].textChanged.connect(lambda: hand.getExtremaInput("X", "Max"))
    Edit_Dict["YMax"].textChanged.connect(lambda: hand.getExtremaInput("Y", "Max"))
    Edit_Dict["ZMax"].textChanged.connect(lambda: hand.getExtremaInput("Z", "Max"))
    Edit_Dict["XUnit"].textChanged.connect(lambda: hand.getUnitInput("X"))
    Edit_Dict["YUnit"].textChanged.connect(lambda: hand.getUnitInput("Y"))
    Edit_Dict["ZUnit"].textChanged.connect(lambda: hand.getUnitInput("Z"))
    Edit_Dict["LineUnit"].textChanged.connect(lambda: hand.getOtherUnitInput("Line"))
    Edit_Dict["GridUnit"].textChanged.connect(lambda: hand.getOtherUnitInput("Grid"))
    Edit_Dict["XCenter"].textChanged.connect(lambda: hand.getCenterInput("X"))
    Edit_Dict["YCenter"].textChanged.connect(lambda: hand.getCenterInput("Y"))
    Edit_Dict["ZCenter"].textChanged.connect(lambda: hand.getCenterInput("Z"))
    Edit_Dict["HorWidth"].textChanged.connect(lambda: hand.getWidthInput("Hor"))
    Edit_Dict["VerWidth"].textChanged.connect(lambda: hand.getWidthInput("Ver"))
    Edit_Dict["XLStart"].textChanged.connect(lambda: hand.getStartEndInput("X", "LStart"))
    Edit_Dict["YLStart"].textChanged.connect(lambda: hand.getStartEndInput("Y", "LStart"))
    Edit_Dict["ZLStart"].textChanged.connect(lambda: hand.getStartEndInput("Z", "LStart"))
    Edit_Dict["XLEnd"].textChanged.connect(lambda: hand.getStartEndInput("X", "LEnd"))
    Edit_Dict["YLEnd"].textChanged.connect(lambda: hand.getStartEndInput("Y", "LEnd"))
    Edit_Dict["ZLEnd"].textChanged.connect(lambda: hand.getStartEndInput("Z", "LEnd"))
    Edit_Dict["XNormDir"].textChanged.connect(lambda: hand.getFloatInput("X", "NormDir"))
    Edit_Dict["YNormDir"].textChanged.connect(lambda: hand.getFloatInput("Y", "NormDir"))
    Edit_Dict["ZNormDir"].textChanged.connect(lambda: hand.getFloatInput("Z", "NormDir"))
    Edit_Dict["XNormNorth"].textChanged.connect(lambda: hand.getFloatInput("X", "NormNorth"))
    Edit_Dict["YNormNorth"].textChanged.connect(lambda: hand.getFloatInput("Y", "NormNorth"))
    Edit_Dict["ZNormNorth"].textChanged.connect(lambda: hand.getFloatInput("Z", "NormNorth"))
    Edit_Dict["Zoom"] = createZoomEdit()
    Edit_Dict["Zoom"].textChanged.connect(lambda: hand.getTextInput("Zoom"))
    Edit_Dict["PlotTitle"] = coolEdit("", placeholder="Plot title",
                                      tooltip="Insert  desired plot title",
                                      width=None)
    Edit_Dict["PlotTitle"].textChanged.connect(lambda: hand.getTextInput("PlotTitle"))
    Edit_Dict["ColorScheme"] = createColorSchemeEdit()
    Edit_Dict["ColorScheme"].textChanged.connect(lambda: hand.getColorInput())
    Edit_Dict["PSlabWidth"] = createSlabWidthEdit()
    Edit_Dict["PSlabWidth"].textChanged.connect(lambda: hand.getTextInput("PSlabWidth"))


def createCenterWidthEdits():
    """Initializes LineEdits to enter values for the center and width of slice
    and projection plots.
    returns:
        lineEdits: List of five LineEdits"""
    Validator = QG.QDoubleValidator()
    lineEdits = []
    for i in range(3):
        LE = coolEdit("0", "0", "Enter center coordinates of the plot")
        LE.setValidator(Validator)
        LE.turnTextBlue()
        lineEdits.append(LE)
    Validator = PosDoubleValidator()
    for i in range(2):
        LE = coolEdit("", "Full domain", "Enter width for the plot")
        LE.setValidator(Validator)
        lineEdits.append(LE)
    return lineEdits


def createExtrema():
    """Initializes LineEdits in a list to enter values for
    minimum and maximum
    returns:
        lineEdits: List of QLineEdits
    """
    # Set Validator so only double values can be entered
    Validator = QG.QDoubleValidator()
    lineEdits = []
    for i in range(6):
        # Tooltip and placeholder are set in sut.resetExtrema or after calc
        LE = coolEdit("")
        LE.turnTextBlue()
        LE.setValidator(Validator)
        lineEdits.append(LE)
    return lineEdits


def createStartEnd():
    """Initializes LineEdits in a list to enter values for start and end point
    when in linePlot mode.
    returns:
        lineEdits: List of QLineEdits
    """
    # Set Validator so only double values can be entered
    Validator = QG.QDoubleValidator()
    placeholders = ["X0", "Y0", "Z0"]
    tooltip = 'Set Start point'
    lineEdits = []
    for i in range(3):
        LE = coolEdit(lineText="0.0", placeholder=placeholders[i],
                      tooltip=tooltip, width=70)
        LE.setValidator(Validator)
        lineEdits.append(LE)
    placeholders = ["X1", "Y1", "Z1"]
    tooltip = 'Set End point'
    for i in range(3):
        LE = coolEdit(lineText="1.0", placeholder=placeholders[i],
                      tooltip=tooltip, width=70)
        LE.setValidator(Validator)
        lineEdits.append(LE)
    return lineEdits


def createColorSchemeEdit(width=150):
    """Initialize LineEdit for selecting the color scheme.
    returns:
        lineEdit: Color scheme line edit with completer
    """
    tooltip = "Set color scheme for third dimension"
    text = "viridis"
    lineEdit = coolEdit(lineText=text, placeholder=text,
                        tooltip=tooltip, width=width)
    completer = QW.QCompleter(validColors)
    completer.setCaseSensitivity(True)
    lineEdit.setCompleter(completer)
    return lineEdit


def createUnits():
    """Initializes LineEdits in a list to enter and display the units currently
    used in the Plot.Connect them to the Dictionary.
    returns:
        lineEdits: List of QLineEdits
    """
    lineText = ""
    placeholders = ["cm", "cm", "g/cm**3", "AU", "AU"]
    lineEdits = []
    for placeholder in placeholders:
        LE = coolEdit(lineText=lineText, placeholder=placeholder, width=150)
        LE.turnTextRed()
        lineEdits.append(LE)
    LE = coolEdit(lineText="", placeholder="AU", width=179)
    LE.turnTextRed()
    LE.setToolTip("Change Unit for start/end point selection.\n"
                  "Dimension has to be length")
    lineEdits.insert(3, LE)  # sorry for this weird implementation
    lineEdits[4].setToolTip("Change Unit for the horizontal and vertical axis."
                            "\nDimension has to be length")
    return lineEdits


def createZoomEdit():
    """Initialize LineEdits for reading out current zoom, panx and pany.
    returns:
        List of those LineEdits
    """
    Validator = PosDoubleValidator()
    placeholder = "Zoom"
    tooltip = "Set Zoom of the plot. Has to be > 0."
    lineEdit = coolEdit(lineText="1.0", placeholder=placeholder,
                        tooltip=tooltip)
    lineEdit.setValidator(Validator)
    return lineEdit


class PosDoubleValidator(QG.QDoubleValidator):
    """Validator for only positive values"""
    def __init__(self):
        super().__init__()

    def validate(self, input_, pos):
        if input_ == "":
            return QG.QDoubleValidator.validate(self, input_, pos)
        try:
            if 0 <= float(input_):
                return QG.QDoubleValidator.validate(self, input_, pos)
            else:
                # This will always be invalid
                return QG.QDoubleValidator.validate(self, "Hallo", pos)
        except ValueError:
            # This will always be invalid
            return QG.QDoubleValidator.validate(self, "Hallo", pos)


class SlabEditValidator(QG.QDoubleValidator):
    def __init__(self):
        super().__init__()

    def validate(self, input_, pos):
        if input_ == "":
            return QG.QDoubleValidator.validate(self, input_, pos)
        try: 
            if 0 <= float(input_) <= 1:
                return QG.QDoubleValidator.validate(self, input_, pos)
            else:
                # This will always be invalid
                return QG.QDoubleValidator.validate(self, "Hallo", pos)
        except ValueError:
            # This will always be invalid
            return QG.QDoubleValidator.validate(self, "Hallo", pos)
        

def createSlabWidthEdit():
    """Initializes a lineEdit to read out the width of the slab the particles
    are to be read out of"""
    Edit = coolEdit("", placeholder="1", tooltip="Percentual width of the "
                    "slab the particles to annotate are taken from", width=100)
    validator = SlabEditValidator()
    Edit.setValidator(validator)
    return Edit


def createNormalVectorEdits():
    """Initializes six LineEdits: three for the normal vector input and three
    for the north vector input."""
    Validator = QG.QDoubleValidator()
    placeholders = ["X: 1.0", "Y: 1.0", "Z: 1.0"]
    tooltip = "Set normal vector direction"
    lineEdits = []
    for i in range(3):
        LE = coolEdit(lineText="1.0", placeholder=placeholders[i],
                      tooltip=tooltip, width=70)
        LE.setValidator(Validator)
        lineEdits.append(LE)
    placeholders = ["X: 1.0", "Y: 0.0", "Z: 0.0"]
    tooltip = "Set north vector direction"
    for i in range(3):
        LE = coolEdit(lineText="0.0", placeholder=placeholders[i],
                      tooltip=tooltip, width=70)
        LE.setValidator(Validator)
        lineEdits.append(LE)
    lineEdits[3].setText("1.0")
    return lineEdits
