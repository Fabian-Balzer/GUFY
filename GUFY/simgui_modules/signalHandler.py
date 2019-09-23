# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Introduces a class that handles all of the signals emitted from the widgets.
Also contains the methods that change their appearance and so on.
"""


from math import ceil
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW
import yt
from simgui_modules import layouts as slay
from tokenize import TokenError
from copy import copy
from simgui_modules.utils import updateNormalAxis, updateComboBoxes, \
    convertToLessThanThree, findIndex, calcExtrema, WorkingException
from simgui_modules.logging import GUILogger
from simgui_modules.plotWindow import PlotWindow
from simgui_modules.configureGUI import config
from simgui_modules.lineEdits import validColors


class SignalHandler(object):
    """Instances of this class are supposed to act as 'punching bags' so
    certain methods can easily be called from anywhere in the program.
    """
    def __init__(self, Window):
        super().__init__()
        self.Param_Dict = Window.Param_Dict
        self.Edit_Dict = Window.Edit_Dict
        self.Button_Dict = Window.Button_Dict
        self.Status_Dict = Window.Status_Dict
        self.ComboBox_Dict = Window.ComboBox_Dict
        self.RadioDict_Dict = Window.RadioDict_Dict
        self.CheckBox_Dict = Window.CheckBox_Dict
        self.Label_Dict = Window.Label_Dict
        self.Wid_Dict = Window.Wid_Dict
        self.Misc_Dict = Window.Misc_Dict
        self.Window = Window

    def makeInitialCopy(self):
        # In these copies we will store the information for changing between
        # Single and Series Mode. We always need to keep the reference to
        # the signal handler, though.
        self.Single_Copy = copy(self.Param_Dict)
        self.Single_Copy["SignalHandler"] = self
        self.Series_Copy = copy(self.Param_Dict)
        self.Series_Copy["EvalMode"] = "Series"
        self.Series_Copy["SignalHandler"] = self

# %% Mainly Button methods:
    def calculateExtrema(self, axis, series=False):
        """Calculate the extrema for the given field if they have not been
        calculated. Change the lineEdits, their placeholders and tooltips
        accordingly.
        FieldMins and FieldMaxs are always kept in the base units of a field.
        Parameters: axis: "X", "Y", "Z" """
        calcMinMax(self.Param_Dict, self.Edit_Dict, self.Button_Dict,
                   self.Status_Dict, self.ComboBox_Dict, axis, series)
        # Also update all of the axes so placeholders/tooltips are updated
        for axis in ["X", "Y", "Z", "N"]:
            self.getAxisInput(axis)

    def setExtrema(self, axis):
        """If the Extrema for the field have been calculated, set the text of min
        and max lineEdits to fieldMin and fieldMax
        Parameters: axis: "X", "Y", "Z" """
        setExtrema(self.Param_Dict, self.Edit_Dict, axis)
        # This way, the extrema will get updated
        getMinMaxInput(self.Param_Dict, self.Edit_Dict, self.CheckBox_Dict,
                       "Min", axis)

# %% Mainly ComboBox methods:
    def getAxisInput(self, axis):
        """Reads out current selection of x, y and z axis and stores them.
        For X, Y and Z axis also update the text edits with units and extrema.
        Parameters: axis: "X", "Y", "Z", "N"
        """
        if axis != "N":
            self.getUnitInput(axis, True)
        change = getAxisInput(self.Param_Dict, self.Button_Dict,
                              self.Edit_Dict, self.ComboBox_Dict, axis,
                              self.CheckBox_Dict, self.Wid_Dict)
        if axis != "N":
            if self.Param_Dict[axis + "Axis"] in \
                    self.Param_Dict["FieldMins"].keys() and change:
                setExtrema(self.Param_Dict, self.Edit_Dict, axis)
            self.getUnitInput(axis, True)
            self.getExtremaInput(axis, "Min")
            self.getExtremaInput(axis, "Max")

    def getWeightField(self, axis):
        """Reads out currently selected Weight field and stores it"""
        getWeightField(self.Param_Dict, self.ComboBox_Dict, self.CheckBox_Dict,
                       axis)
        self.getUnitInput(axis, True)
        self.getAxisInput("Z")

    def getTimeQuantityInput(self):
        """Reads out the selected value for the TimeQuantity ComboBox"""
        getTimeQuantityInput(self.Param_Dict, self.ComboBox_Dict)


# %% Mainly LineEdit methods
    def getExtremaInput(self, axis, mode):
        """Read out current selection of min and max coordinates and store them.
        If the unit is changed, change them as well.
        Also provide visual feedback on wether min/max for the shown field have
        been calculated and if the user is out of the bounds.
        Parameters:
            axis: "X", "Y", "Z"
            mode: "Min" for minimum,
                  "Max" for maximum
        """
        getMinMaxInput(self.Param_Dict, self.Edit_Dict, self.CheckBox_Dict,
                       mode, axis)

    def getUnitInput(self, axis, fieldChange=False):
        """Reads out current selection of units and stores them in
        a list in the Parameter Dictionary.
        Parameters: axis: "X", "Y", "Z"
                fieldChange: bool; true if the field has changed so no
                                unit conversion takes place
        """
        getUnitInput(self.Param_Dict, self.Edit_Dict,
                     self.Label_Dict, axis, self.ComboBox_Dict, fieldChange)

    def getOtherUnitInput(self, mode):
        """When Line or Grid Unit is chosen, check the validity of it.
        Parameters:
            mode: "Line", "Grid"
        """
        getLineGridUnitInput(self.Param_Dict, self.Edit_Dict,
                             self.Label_Dict, mode)
        if mode == "Line":
            setLineLengthLabel(self.Param_Dict, self.Label_Dict)

    def getCenterInput(self, axis):
        """Reads out the input of the center edits and gives visual feedback.
        Parameters: axis: "X", "Y", "Z"
        """
        getCenterInput(self.Param_Dict, self.Edit_Dict, axis)

    def getStartEndInput(self, axis, mode):
        """Reads out current selection of start and end points and stores them
        in a list in the Parameter Dictionary.
        Parameters: axis: "X", "Y", "Z"
            mode: "LStart" and "LEnd"
        """
        self.getFloatInput(axis, mode)
        setLineLengthLabel(self.Param_Dict, self.Label_Dict)

    def getFloatInput(self, axis, mode):
        """Reads out the text of the LineEdit given through the combination of
        axis and mode and saves it as a float in Param_Dict.
        Parameters:
            axis: str: "X", "Y" or "Z"
            mode: str: "LStart", "LEnd", "NormDir", "NormNorth"
        """
        getFloatInput(self.Param_Dict, self.Edit_Dict, axis, mode)

    def getTextInput(self, key):
        """Reads out the text of the LineEdit given through key and saves it
        in Param_Dict"""
        getTextInput(self.Param_Dict, self.Edit_Dict, key)

    def getColorInput(self):
        """Reads out the color scheme input and gives visual feedback."""
        getColorInput(self.Param_Dict, self.Edit_Dict)

    def getWidthInput(self, orientation):
        """Reads out the width input and gives visual feedback.
        Parameters:
            orientation: "Hor" or "Ver"
        """
        getWidthInput(self.Param_Dict, self.Edit_Dict, orientation)

# %% Mainly CheckBox Methods
    def getAnnotationInput(self, key):
        """Read out any mundane checkbox-input and store it in Param_Dict."""
        getAnnotationInput(self.Param_Dict, self.CheckBox_Dict, key)

    def getDomainDivInput(self):
        self.getAnnotationInput("DomainDiv")
        saveNormedLength(self.Param_Dict)  # so in the normed key gets added
        # We need to update the unit and convert min/max as well
        if self.Param_Dict["WeightField"] is None:
            self.getUnitInput("Z", fieldChange=False)

    def getAddProfileInput(self):
        self.getAnnotationInput("AddProfile")
        freezeXAxis(self.Param_Dict, self.CheckBox_Dict, self.ComboBox_Dict,
                    self.Edit_Dict, self.Button_Dict)

    def getParticleInput(self):
        self.getAnnotationInput("ParticlePlot")
        freezeNormVecMode(self.Param_Dict, self.RadioDict_Dict)
        updateComboBoxes(self.Param_Dict, self.ComboBox_Dict)
        for axis in ["X", "Y", "Z"]:
            self.getAxisInput(axis)

# %% Mainly RadioButton Methods
    def changeEvalMode(self):
        """Reads out current Evaluation Mode and stores it in Param_Dict."""
        change = changeEvalMode(self.Param_Dict, self.RadioDict_Dict)
        changeOpenButton(self.Param_Dict, self.Button_Dict, self.Status_Dict,
                         self.Wid_Dict)
        if change:
            if self.Param_Dict["EvalMode"] == "Single":
                self.Series_Copy = copy(self.Param_Dict)
                self.Series_Copy["EvalMode"] = "Series"
                self.Series_Copy["SignalHandler"] = self
                self.restoreFromParam_Dict(self.Single_Copy)
            elif self.Param_Dict["EvalMode"] == "Series":
                self.Single_Copy = copy(self.Param_Dict)
                self.Single_Copy["EvalMode"] = "Single"
                self.Single_Copy["SignalHandler"] = self
                self.restoreFromParam_Dict(self.Series_Copy)

    def changeDimensions(self):
        """When 1D or 2D is pressed, save parameters of the mode and toggle"""
        getDimensionInput(self.Param_Dict, self.RadioDict_Dict)
        getPlotModeInput(self.Param_Dict, self.RadioDict_Dict)
        self.setPlotOptions()

    def setPlotOptions(self):
        """Checks for currently active option and properly sets the options"""
        changeDimensions(self.Param_Dict, self.Wid_Dict)
        # Convenient way of calling the desired changeTo-function
        eval("self.changeTo" + self.Param_Dict["PlotMode"] + "()")
        # Also update all of the axes so placeholders/tooltips are updated
        if self.Param_Dict["PlotMode"] == "Projection":
            self.getAxisInput("Z")
            self.getAxisInput("N")
        else:
            for axis in ["N", "X", "Y", "Z"]:
                self.getAxisInput(axis)
        freezeXAxis(self.Param_Dict, self.CheckBox_Dict, self.ComboBox_Dict,
                    self.Edit_Dict, self.Button_Dict)
        self.getWidthInput("Hor")
        self.getWidthInput("Ver")
        self.changeNormVecMode()

    def changeNormVecMode(self):
        """Read out the currently chosen mode for the normal vector
        (axis-aligned or off-axis), store it in Param_Dict and disable the
        widgets accordingly"""
        getNormVecModeInput(self.Param_Dict, self.RadioDict_Dict)
        prepareForNormVec(self.Param_Dict, self.ComboBox_Dict, self.Wid_Dict,
                          self.CheckBox_Dict, self.Edit_Dict)

# %% Mainly Layout-related methods
    def changeToLine(self):
        changeToLine(self.Param_Dict, self.Wid_Dict, self.CheckBox_Dict,
                     self.Edit_Dict, self.Button_Dict)
        setLineLengthLabel(self.Param_Dict, self.Label_Dict)

    def changeToPhase(self):
        changeToPhase(self.Param_Dict, self.Wid_Dict, self.CheckBox_Dict,
                      self.ComboBox_Dict, self.Edit_Dict, self.Button_Dict)

    def changeToProfile(self):
        changeToProfile(self.Param_Dict, self.Wid_Dict, self.CheckBox_Dict,
                        self.ComboBox_Dict, self.Misc_Dict, self.Edit_Dict,
                        self.Button_Dict)

    def changeToProjection(self):
        changeToProjection(self.Param_Dict, self.Wid_Dict, self.CheckBox_Dict,
                           self.ComboBox_Dict, self.Button_Dict,
                           self.Edit_Dict)

    def changeToSlice(self):
        changeToSlice(self.Param_Dict, self.Wid_Dict, self.CheckBox_Dict,
                      self.ComboBox_Dict, self.Button_Dict, self.Edit_Dict)

# %% Miscellaneous methods
    def getProfOfEveryInput(self):
        getProfOfEveryInput(self.Param_Dict, self.Misc_Dict)

    def getSliderInput(self, value=None, seriesEval=False):
        """Checks the current Slider Input and changes the current File"""
        getSliderInput(self.Param_Dict, self.Label_Dict, self.Misc_Dict,
                       value=value, seriesEval=seriesEval)
        if self.Param_Dict["PlotMode"] == "Profile":
            self.changeToProfile()

    def restoreFromParam_Dict(self, Param_Dict_Copy):
        """Restores the desired plot settings from the copy of the Param_Dict
        or the given Param_Dict."""
        self.Param_Dict["CurrentPlotWindow"].hide()
        self.Window.Param_Dict = copy(Param_Dict_Copy)
        self.Window.Param_Dict["SignalHandler"] = self
        self.Param_Dict = self.Window.Param_Dict
        restoreFromParam_Dict(Param_Dict_Copy, self.CheckBox_Dict,
                              self.ComboBox_Dict, self.Edit_Dict,
                              self.Label_Dict, self.RadioDict_Dict,
                              self.Button_Dict, self.Misc_Dict, self.Wid_Dict)
        self.changeDimensions()
        self.getWidthInput("Hor")
        self.getWidthInput("Ver")
        for axis in ["X", "Y", "Z"]:
            self.getCenterInput(axis)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %% Button stuff
def calcMinMax(Param_Dict, Edit_Dict, Button_Dict, Status_Dict, ComboBox_Dict,
               axis, series=False):
    """Calculate the extrema for the given field if they have not been
    calculated. Change the lineEdits, their placeholders and tooltips
    accordingly.
    FieldMins and FieldMaxs are always kept in the base units of a field.
    Parameters:
        Param_Dict: Parameter Dictionary
        Edit_Dict: LineEdit Dictionary
        axis: "X", "Y" and "Z" for the corresponding field
    """
    QW.QApplication.setOverrideCursor(QC.Qt.WaitCursor)
    isProj = Param_Dict["PlotMode"] == "Projection"
    weightNone = Param_Dict["WeightField"] is None
    projectionCondition = isProj and weightNone
    projString = ""
    if projectionCondition:
        projString = "projected "
    field = Param_Dict[axis + "Axis"]
    seriesString = "Extrema"
    if series:
        seriesString = "Global extrema"
    GUILogger.info(f"Calculating {seriesString.lower()} for {projString}{field}...")
    # These are the keys needed out of the Param_Dict:
    ds = Param_Dict["CurrentDataSet"]
    minLineEdit = Edit_Dict[axis + "Min"]
    maxLineEdit = Edit_Dict[axis + "Max"]
    unit = Param_Dict[axis + "Unit"]
    try:
        Min, Max = calcExtrema(Param_Dict, ds, field, projectionCondition)
    except WorkingException:
        return
    if series:
        globMin, globMax = Min, Max
        for ds in Param_Dict["DataSeries"]:
                Min, Max = calcExtrema(Param_Dict, ds, field, projectionCondition)
                globMin, globMax = min(Min, globMin), max(Max, globMax)
        Min, Max = globMin, globMax
    if projectionCondition:
        field = "Proj" + field
    # Convert this YTArray to the selected unit of the field
    # (since the dimensions are checked on input, we shouldn't have
    # dimensionality problems)
    Param_Dict["FieldMins"][field] = Min.to_value(Param_Dict["FieldUnits"][field])
    Param_Dict["FieldMaxs"][field] = Max.to_value(Param_Dict["FieldUnits"][field])
    if Param_Dict["PlotMode"] == "Projection" and Param_Dict["DomainDiv"]:
        height = Param_Dict["FieldMaxs"]["DomainHeight"] - Param_Dict["FieldMins"]["DomainHeight"]
        Min, Max = Min/height, Max/height
    minCodeUnits = Min.to_value(unit)
    minRounded = f"{minCodeUnits:.3g}"
    maxCodeUnits = Max.to_value(unit)
    maxRounded = f"{maxCodeUnits:.3g}"
    minLineEdit.setText(minRounded)
    maxLineEdit.setText(maxRounded)
    minLineEdit.setPlaceholderText(minRounded)
    minLineEdit.setToolTip(f"Supports a value between {minRounded} and {maxRounded}")
    maxLineEdit.setPlaceholderText(maxRounded)
    maxLineEdit.setToolTip(f"Supports a value between {minRounded} and {maxRounded}")
    GUILogger.debug("fieldMinMax: {0} {1}, {2} {1}".format(Param_Dict["FieldMins"][field],
                    Param_Dict["FieldUnits"][field], Param_Dict["FieldMins"][field]))
    GUILogger.debug("CurrentMinMax: {0} {1}, {2} {1}".format(minRounded, unit, maxRounded))
    Button_Dict[axis + "Calc"].setToSetExtrema(Param_Dict, axis)
    GUILogger.info(f"{seriesString} for {projString}{Param_Dict[axis + 'Axis']} have been calculated.")
    if Param_Dict["EvalMode"] == "Series" and not series:
        GUILogger.warning("These are only the extrema of "
                          f"{projString + Param_Dict[axis + 'Axis']} for the "
                          "current dataset, but are saved for the whole series")
        GUILogger.log(29, "Press the button right of <b>Set Extrema</b> to "
                      "open options for calculating the global extrema.")
    QW.QApplication.restoreOverrideCursor()
#    GUILogger.debug(f"The width is now {Param_Dict['HorWidth']}")


def setExtrema(Param_Dict, Edit_Dict, axis):
    """If the Extrema for the field have been calculated, set the text of min
    and max lineEdits to fieldMin and fieldMax
    Parameters:
        Param_Dict: For Field, FieldMins, FieldMaxs, AxisUnit
        Edit_Dict: For Min and Max LineEdits
        axis: "X", "Y", "Z"
    """
    field = Param_Dict[axis + "Axis"]
    if Param_Dict["PlotMode"] == "Projection" and Param_Dict["WeightField"] is None:
        field = "Proj" + field
        if Param_Dict["DomainDiv"]:
            field = "Norm" + field
    fieldBaseUnit = Param_Dict["FieldUnits"][field]
    newUnit = Param_Dict[axis + "Unit"]
    try:
        fieldMin = Param_Dict["FieldMins"][field]
        fieldMax = Param_Dict["FieldMaxs"][field]
        fieldMin = yt.YTQuantity(fieldMin, fieldBaseUnit).to_value(newUnit)
        fieldMax = yt.YTQuantity(fieldMax, fieldBaseUnit).to_value(newUnit)
        fieldMin = "{0:.3g}".format(fieldMin)
        fieldMax = "{0:.3g}".format(fieldMax)
        Edit_Dict[axis + "Min"].setText(fieldMin)
        Edit_Dict[axis + "Max"].setText(fieldMax)
    except KeyError:
        pass


# %% ComboBox stuff
def getAxisInput(Param_Dict, Button_Dict, Edit_Dict, ComboBox_Dict, axis,
                 CheckBox_Dict, Wid_Dict):
    """Reads out current selection of x, y and z axis and stores them.
    Also changes entries of min, max, unit and log according to predetermined
    values.
    Parameters:
        Param_Dict: Parameter Dictionary
        axesBox: comboBox with current Axis that has changed
        axis: "X", "Y" and "Z" for the corresponding field
        Edit_Dict: if normal axis is changed we need to pass it
    returns: True if the field has changed, else False
    """
    oldField = Param_Dict[axis + "Axis"]
    field = ComboBox_Dict[axis + "Axis"].currentText()
    if field == "":
        return False  # In this case, we don't want to do anything
    else:
        Param_Dict[axis + "Axis"] = field
        if Param_Dict["isValidFile"]:
            if axis != "N":
                addFieldUnit(Param_Dict, Edit_Dict, axis)
                checkCalculated(Param_Dict, Button_Dict, Edit_Dict,
                                axis, ComboBox_Dict, CheckBox_Dict)
            elif axis == "N":
                getDomainConstraints(Param_Dict, Edit_Dict)
            if Param_Dict["PlotMode"] == "Projection":
                saveNormedLength(Param_Dict)
        if axis == "X":
            if field == "time":  # We can't have time as x-axis and have plots of multiple times at once.
                CheckBox_Dict["TimeSeriesProf"].setChecked(False)
                CheckBox_Dict["TimeSeriesProf"].setDisabled(True)
                Button_Dict["PlotAll"].setDisabled(True)
                slay.hideShowLabels(Wid_Dict["YAxis"], 2, 3, hide=False)
                CheckBox_Dict["Timestamp"].setHidden(True)
                ComboBox_Dict["TimeQuantity"].currentIndexChanged.emit(0)
            else:
                CheckBox_Dict["TimeSeriesProf"].setEnabled(True)
                Button_Dict["PlotAll"].setEnabled(True)
                slay.hideShowLabels(Wid_Dict["YAxis"], 2, 3, hide=True)
                CheckBox_Dict["Timestamp"].setHidden(False)
                ComboBox_Dict["YWeight"].setEnabled(True)
        return oldField != field


def addFieldUnit(Param_Dict, Edit_Dict, axis):
    """Adds an entry with the current field reference unit to the FieldUnits
    dictionary.
    If projection mode is enabled, multiply by length dimension
    Parameters:
        Param_Dict: Parameter Dictionary for getting selected field and setting
                    unit
    """
    field = Param_Dict[axis + "Axis"]
    # if we've already calculated the base unit, we don't need to do anything
    if field in Param_Dict["FieldUnits"].keys():
        pass
    else:
        # Convert the unit currently used as the axis into a yt quantity
        ds = Param_Dict["CurrentDataSet"]
        # We need to use the eval-command here since we only have the field as
        # a string. There are other methods that are significantly slower.
        if Param_Dict["ParticlePlot"]:
            unit = eval("yt.YTQuantity(ds.arr(1, "
                        "ds.fields.io." + field + ".units)).units")
        else:
            unit = eval("yt.YTQuantity(ds.arr(1, "
                        "ds.fields.gas." + field + ".units)).units")
        Param_Dict["FieldUnits"][field] = unit  # set the unit anyways to prevent key errors later
        Param_Dict["FieldUnits"]["Proj" + field] = unit*yt.units.unit_object.Unit("cm")
        if Param_Dict["PlotMode"] == "Projection" and not Param_Dict["DomainDiv"] and Param_Dict["WeightField"] is None:
            unit = str(unit) + "*cm"
        Param_Dict[axis + "Unit"] = str(unit)
    if Param_Dict["PlotMode"] == "Projection" and not Param_Dict["DomainDiv"] and Param_Dict["WeightField"] is None:
        field = "Proj" + field
    fieldUnit = Param_Dict["FieldUnits"][field]
    Edit_Dict[axis + "Unit"].setText(Param_Dict[axis + "Unit"])
    Edit_Dict[axis + "Unit"].setPlaceholderText(str(fieldUnit))
    Edit_Dict[axis + "Unit"].setToolTip("Set unit of this field to " +
                                        str(fieldUnit.dimensions) + "-dimension")


def checkCalculated(Param_Dict, Button_Dict, Edit_Dict, axis, ComboBox_Dict,
                    CheckBox_Dict):
    """Checks wether the extrema for the newly selected field have been
    calculated and changes the entries of the line edits accordingly.
    Parameters:
        Param_Dict: Parameter Dictionary
        Button_Dict: The Buttons to calculate the extrema need to be shown if
                     extrema are not available
        Edit_Dict: To change the necessary lineEdits
        axis: "X", "Y" and "Z" for the corresponding field
    """
    field = Param_Dict[axis + "Axis"]
    if Param_Dict["PlotMode"] == "Projection" and not Param_Dict["DomainDiv"] and Param_Dict["WeightField"] is None:
        field = "Proj" + field
    minEdit = Edit_Dict[axis + "Min"]
    maxEdit = Edit_Dict[axis + "Max"]
    Button_Dict[axis + "Recalc"].setVisible(Param_Dict["isValidSeries"])
    if Param_Dict[axis + "Axis"] == "time":
        Button_Dict[axis + "Recalc"].hide()
    if field in Param_Dict["FieldMins"].keys():
        Button_Dict[axis + "Calc"].setToSetExtrema(Param_Dict, axis)
        fieldMin = Param_Dict["FieldMins"][field]
        fieldMax = Param_Dict["FieldMaxs"][field]
        fieldUnit = Param_Dict["FieldUnits"][field]
        unit = Param_Dict[axis + "Unit"]
        fieldMin = yt.YTQuantity(fieldMin, fieldUnit).to_value(unit)
        fieldMax = yt.YTQuantity(fieldMax, fieldUnit).to_value(unit)
        minEdit.setPlaceholderText("{0:.3g}".format(fieldMin))
        minEdit.setToolTip("Supports a value between {0:.3g} and {1:.3g}".format(fieldMin, fieldMax))
        maxEdit.setPlaceholderText("{0:.3g}".format(fieldMax))
        maxEdit.setToolTip("Supports a value between {0:.3g} and {1:.3g}".format(fieldMin, fieldMax))
    else:
        Button_Dict[axis + "Calc"].setToCalculate(Param_Dict, axis)
        minEdit.setPlaceholderText("default")
        minEdit.setToolTip("Press 'Calculate Extrema' to get Extrema for " + field)
        minEdit.turnTextBlue()
        maxEdit.setPlaceholderText("default")
        maxEdit.setToolTip("Press 'Calculate Extrema' to get Extrema for " + field)
        maxEdit.turnTextBlue()


def getDomainConstraints(Param_Dict, Edit_Dict):
    """Gets the domain constraints orthogonal to the plane of slicing.
    Parameters:
        Param_Dict: For getting the n-axis and saving the constraints
                    into the FieldMin/Max dictionaries
        Edit_Dict: For setting the width
    """
#    GUILogger.debug(f"Before: {Param_Dict['HorWidth']}, {Param_Dict['VerWidth']}")
    ds = Param_Dict["CurrentDataSet"]
    minArray = ds.domain_left_edge
    maxArray = ds.domain_right_edge
    widthArray = ds.domain_width
    axis = Param_Dict["NAxis"]
    if Param_Dict["Geometry"] == "cartesian":
        n = ["x", "y", "z"].index(axis)
        x = convertToLessThanThree(n+1)
        y = convertToLessThanThree(n+2)
    elif Param_Dict["Geometry"] == "cylindrical":
        n = ["r", "z", "theta"].index(axis)
        x = convertToLessThanThree(n+1)
        y = convertToLessThanThree(n+2)
    # Unilike other entries in FieldMins, height gets saved with code_unit
    Param_Dict["FieldMins"]["DomainHeight"] = minArray[n]
    Param_Dict["FieldMaxs"]["DomainHeight"] = maxArray[n]
    if axis == "z":
        # In this case, everything is projected into a plane where the
        # maximum radial extent is of interest
        ds = Param_Dict["CurrentDataSet"]
        widthArray = [maxArray[0]*2]
        x, y = 0, 0
    elif axis == "r":
        widthArray = yt.YTArray([0, 0, 0], "m")
    Param_Dict["HorDomainWidth"] = widthArray[x]
    Param_Dict["VerDomainWidth"] = widthArray[y]
    unit = Param_Dict["GridUnit"]
    maxHor = widthArray[x].to_value(unit)
    maxVer = widthArray[y].to_value(unit)
    try:
        if float(Edit_Dict["HorWidth"].text()) == 0.:
            Param_Dict["HorWidth"] = maxHor
            Edit_Dict["HorWidth"].setText("")
    except ValueError:
        Param_Dict["HorWidth"] = maxHor
    try:
        if float(Edit_Dict["VerWidth"].text()) == 0.:
            Param_Dict["VerWidth"] = maxVer
            Edit_Dict["VerWidth"].setText("")
    except ValueError:
        Param_Dict["VerWidth"] = maxVer
    Edit_Dict["HorWidth"].setToolTip("Set the horizontal width to a value "
                                     f"between 0 and {maxHor:.3g} {unit}.")
    Edit_Dict["VerWidth"].setToolTip("Set the vertical width to a value "
                                     f"between 0 and {maxVer:.3g} {unit}.")
#    GUILogger.debug(f"After: {Param_Dict['HorWidth']}, {Param_Dict['VerWidth']}")


def saveNormedLength(Param_Dict):
    """Also save the normalized projected field length"""
    field = "Proj" + Param_Dict["ZAxis"]
    if field in Param_Dict["FieldMins"].keys():
        height = abs(Param_Dict["FieldMaxs"]["DomainHeight"] - Param_Dict["FieldMins"]["DomainHeight"])
        height = height.to_value("cm")
        Param_Dict["FieldMins"]["Norm" + field] = Param_Dict["FieldMins"][field]/height
        Param_Dict["FieldMaxs"]["Norm" + field] = Param_Dict["FieldMaxs"][field]/height
    Param_Dict["FieldUnits"]["Norm" + field] = Param_Dict["FieldUnits"][Param_Dict["ZAxis"]]


def convertNormalInputToIndex(Param_Dict):
    """Converts the current normal axis input to an index.
    returns:
        n: index of current normal axis
    """
    axis = Param_Dict["NAxis"]
    if Param_Dict["Geometry"] == "cartesian":
        n = ["x", "y", "z"].index(axis)
    elif Param_Dict["Geometry"] == "cylindrical":
        n = ["r", "z", "theta"].index(axis)
    return n


def getWeightField(Param_Dict, ComboBox_Dict, CheckBox_Dict, axis):
    """Reads out currently selected weight field and puts it to Param_Dict.
    The weight field should always be the same for Y and Z axis."""
    field = ComboBox_Dict[axis + "Weight"].currentText()
    Param_Dict["WeightField"] = field
    if ComboBox_Dict[axis + "Weight"].currentText() == "None":
        Param_Dict["WeightField"] = None
        CheckBox_Dict["DomainDiv"].setEnabled(True)
    else:
        CheckBox_Dict["DomainDiv"].setChecked(False)
        CheckBox_Dict["DomainDiv"].setEnabled(False)


def getTimeQuantityInput(Param_Dict, ComboBox_Dict):
    """Reads out the input of the time quantity ComboBox and enables/disables
    the weight field accordingly"""
    timeQuan = ComboBox_Dict["TimeQuantity"].currentText()
    Param_Dict["TimeQuantity"] = timeQuan
    hasWeight = timeQuan in ["weighted_average", "weighted_variance"]
    ComboBox_Dict["YWeight"].setEnabled(hasWeight)


# %% LineEdit stuff
def getMinMaxInput(Param_Dict, Edit_Dict, CheckBox_Dict, mode, axis):
    """Read out current selection of min and max coordinates and store them.
    If the unit is changed, change them as well.
    Also provide visual feedback on whether min/max for the shown field have
    been calculated and if the user is out of the bounds.
    Parameters:
        Param_Dict: Parameter Dictionary. We modify the AxisMin and AxisMax
                    and access FieldMins and FieldMaxs
        LineEdit: LineEdit that the text is read of
        mode:
            "Min" for minimum,
            "Max" for maximum
        axis: "X", "Y" and "Z" for the corresponding field
        CheckBox_Dict: To enable and disable logarithm checkboxes in some cases
    """
    field = Param_Dict[axis + "Axis"]
    plotmode = Param_Dict["PlotMode"]
    LineEdit = Edit_Dict[axis + mode]
    if plotmode == "Projection" and Param_Dict["WeightField"] is None:
        field = "Proj" + field  # In case of projection
        if Param_Dict["DomainDiv"]:
            field = "Norm" + field  # In case the user wants to normalize proj
    # We only need to do the checking if the user already calculated the extrema
    if field in Param_Dict["FieldMins"].keys():
        LineEdit.setEnabled(True)
        fieldMin = Param_Dict["FieldMins"][field]
        fieldMax = Param_Dict["FieldMaxs"][field]
        fieldBaseUnit = Param_Dict["FieldUnits"][field]
        newUnit = Param_Dict[axis + "Unit"]
        fieldMin = yt.YTQuantity(fieldMin, fieldBaseUnit).to_value(newUnit)
        fieldMax = yt.YTQuantity(fieldMax, fieldBaseUnit).to_value(newUnit)
        fieldMin = float(f"{fieldMin:.3g}")
        fieldMax = float(f"{fieldMax:.3g}")
        try:
            inputNumber = float(LineEdit.text())
            if mode == "Min":
                if (inputNumber >= fieldMin) and (inputNumber <= fieldMax):
                    LineEdit.turnTextBlack()
                else:
                    LineEdit.turnTextRed()
            if mode == "Max":
                if (inputNumber >= fieldMin) and (inputNumber <= fieldMax):
                    LineEdit.turnTextBlack()
                else:
                    LineEdit.turnTextRed()
        except ValueError:
            LineEdit.turnTextRed()
            if mode == "Min":
                inputNumber = fieldMin
            elif mode == "Max":
                inputNumber = fieldMax
        Param_Dict[axis + mode] = inputNumber
    else:
        LineEdit.turnTextBlue()
        LineEdit.setEnabled(False)
    # In some cases, we need to prevent the user setting an axis to log
    try:
        if min(Param_Dict[axis + "Min"], Param_Dict[axis + "Max"]) <= 0:
            if plotmode == "Profile" or plotmode == "Phase":
                CheckBox_Dict[axis + "Log"].setChecked(False)
                CheckBox_Dict[axis + "Log"].setEnabled(False)
            else:
                CheckBox_Dict[axis + "Log"].setEnabled(True)
        else:
            CheckBox_Dict[axis + "Log"].setEnabled(True)
    except TypeError:
        pass


def getUnitInput(Param_Dict, Edit_Dict, Label_Dict, axis, ComboBox_Dict,
                 fieldChange=False):
    """Reads out current selection of units and stores them in the Parameter
    Dictionary. Converts the Line Edit texts if necessary.
    Parameters:
        Param_Dict: Parameter Dictionary
        LineEdit: LineEdit that the text is read of
        axis: "X", "Y" and "Z" for the corresponding field
        Edit_Dict: For mins and maxs to be passed to changeMinMaxByUnit
        fieldChange: Bool that is used whenever the fields change
    """
    oldUnit = Param_Dict[axis + "Unit"]
    field = ComboBox_Dict[axis + "Axis"].currentText()
    if field == '':
        return
    LineEdit = Edit_Dict[axis + "Unit"]
    if Param_Dict["PlotMode"] == "Projection" and not Param_Dict["DomainDiv"] and Param_Dict["WeightField"] is None:
        field = "Proj" + field
    # We have the base unit of the field saved in the FieldUnits dictionary
    try:
        fieldUnit = Param_Dict["FieldUnits"][field]
    except KeyError:
        if Param_Dict["TestingMode"]:
            GUILogger.debug(f"Couldn't find the field unit for {field}.")
        return
    try:
        textUnit = yt.YTQuantity(1, LineEdit.text()).units
        if fieldUnit.same_dimensions_as(textUnit):
            LineEdit.turnTextBlack()
            Param_Dict[axis + "Unit"] = LineEdit.text()
        else:
            LineEdit.turnTextRed()
            Param_Dict[axis + "Unit"] = str(fieldUnit)
    except (yt.units.unit_object.UnitParseError, AttributeError, TokenError, TypeError):
        LineEdit.turnTextRed()
        Param_Dict[axis + "Unit"] = str(fieldUnit)
    # We only want to convert mins and maxs if we didn't change dimensions
    if not fieldChange and Param_Dict["isValidFile"]:
        changeMinMaxByUnit(Param_Dict, Edit_Dict, axis, oldUnit)
    Label_Dict[axis + "MinUnit"].setText(Param_Dict[axis + "Unit"])
    Label_Dict[axis + "MaxUnit"].setText(Param_Dict[axis + "Unit"])
    LineEdit.setPlaceholderText(Param_Dict[axis + "Unit"])


def changeMinMaxByUnit(Param_Dict, Edit_Dict, axis, oldUnit):
    """After the unit has been read out, change the minimum and maximum
    according to the unit currently chosen on the displayed text.
    Parameters:
        Param_Dict:  Parameter Dictionary for reading out current state
        Edit_Dict: We want to change the texts of the lineEdits min and max
        axis: "X", "Y" and "Z" for the corresponding field
        oldUnit: The old unit that was used for this field before
    """
    # These are the relevant keys used
    field = Param_Dict[axis + "Axis"]
    ds = Param_Dict["CurrentDataSet"]
    if Param_Dict["PlotMode"] == "Projection" and Param_Dict["WeightField"] is None:
        field = "Proj" + field
        if Param_Dict["DomainDiv"]:
            field = "Norm" + field
    # convert the units to something yt can read
    oldUnit = yt.YTQuantity(ds.quan(1, oldUnit)).units
    newUnit = Param_Dict[axis + "Unit"]
    newUnit = yt.YTQuantity(ds.quan(1, newUnit)).units
    try:
        minVal = float(Edit_Dict[axis + "Min"].text())
        minValid = True
    except ValueError:
        minValid = False
    try:
        maxVal = float(Edit_Dict[axis + "Max"].text())
        maxValid = True
    except ValueError:
        maxValid = False
    if Param_Dict["isValidFile"]:
        height = abs(Param_Dict["FieldMaxs"]["DomainHeight"] - Param_Dict["FieldMins"]["DomainHeight"])
    else:
        height = 1
    # We need to do some things differently if we normalize projection
    if minValid:
        if (newUnit/oldUnit).same_dimensions_as(yt.units.unit_object.Unit("cm")):
            minVal = (yt.YTQuantity(minVal, oldUnit)*height).to_value(newUnit)
        elif (newUnit/oldUnit).same_dimensions_as(yt.units.unit_object.Unit("1/cm")):
            minVal = (yt.YTQuantity(minVal, oldUnit)/height).to_value(newUnit)
        else:
            minVal = yt.YTQuantity(minVal, oldUnit).to_value(newUnit)
        Edit_Dict[axis + "Min"].setText("{0:.3g}".format(minVal))
    if maxValid:
        if (newUnit/oldUnit).same_dimensions_as(yt.units.unit_object.Unit("cm")):
            maxVal = (yt.YTQuantity(maxVal, oldUnit)*height).to_value(newUnit)
        elif (newUnit/oldUnit).same_dimensions_as(yt.units.unit_object.Unit("1/cm")):
            maxVal = (yt.YTQuantity(maxVal, oldUnit)/height).to_value(newUnit)
        else:
            maxVal = yt.YTQuantity(maxVal, oldUnit).to_value(newUnit)
        Edit_Dict[axis + "Max"].setText("{0:.3g}".format(maxVal))
    if field in Param_Dict["FieldMins"].keys():
        fieldMin = yt.YTQuantity(Param_Dict["FieldMins"][field],
                                       Param_Dict["FieldUnits"][field]).to_value(newUnit)
        fieldMax = yt.YTQuantity(Param_Dict["FieldMaxs"][field],
                                       Param_Dict["FieldUnits"][field]).to_value(newUnit)
        Edit_Dict[axis + "Min"].setPlaceholderText("{0:.3g}".format(fieldMin))
        Edit_Dict[axis + "Min"].setToolTip("Supports a value between {0:.3g} "
                                           "and {1:.3g} {2}".format(fieldMin, fieldMax, str(newUnit)))
        Edit_Dict[axis + "Max"].setPlaceholderText("{0:.3g}".format(fieldMax))
        Edit_Dict[axis + "Max"].setToolTip("Supports a value between {0:.3g} "
                                           "and {1:.3g} {2}".format(fieldMin, fieldMax, str(newUnit)))


def getLineGridUnitInput(Param_Dict, Edit_Dict, Label_Dict, mode):
    """When the Line or Grid Unit is chosen, check the validity of it.
    Parameters:
        mode: "Line", "Grid"
    """
    LineEdit = Edit_Dict[mode + "Unit"]
    oldUnit = Param_Dict[mode + "Unit"]
    # reference unit
    fieldUnit = yt.YTQuantity(1, "au").units
    try:
        textUnit = yt.YTQuantity(1, LineEdit.text()).units
        if fieldUnit.same_dimensions_as(textUnit):
            LineEdit.turnTextBlack()
            newUnit = LineEdit.text()
        else:
            LineEdit.turnTextRed()
            newUnit = str(fieldUnit)
    except (yt.units.unit_object.UnitParseError, AttributeError, TypeError):
        LineEdit.turnTextRed()
        newUnit = str(fieldUnit)
    Param_Dict[mode + "Unit"] = newUnit
    if mode == "Grid":
        for axis in ["X", "Y", "Z"]:
            Label_Dict[axis + "CenUnit"].setText(newUnit)
        if Param_Dict["Geometry"] == "cylindrical" and axis == "Z":
            Label_Dict["ZCenUnit"].setText("")
        Label_Dict["HorWidthUnit"].setText(newUnit)
        Label_Dict["VerWidthUnit"].setText(newUnit)
    changeFieldByUnit(Param_Dict, Edit_Dict, mode, oldUnit, newUnit)


def changeFieldByUnit(Param_Dict, Edit_Dict, mode, oldUnit, newUnit):
    """After the unit has been read out, change the start/end points for line
    plots or the lineEdits corresponding to the grid unit.
    Parameters:
        Param_Dict:  Parameter Dictionary for reading out current state
        Edit_Dict: We want to change the texts of some of the lineEdits
        mode: "Line", "Grid"
        oldUnit: The old unit that was used for this field before
        newUnit: The unit to convert the text to
    """
    # These are the relevant keys used
    if mode == "Line":
        keys = ["XLStart", "YLStart", "ZLStart", "XLEnd", "YLEnd", "ZLEnd"]
    if mode == "Grid":
        keys = ["XCenter", "YCenter", "ZCenter", "HorWidth", "VerWidth"]
    for key in keys:
        try:
            value = float(Edit_Dict[key].text())
        except ValueError:
            value = 0.0
        if Param_Dict["Geometry"] == "cylindrical" and key == "ZCenter":  # no line input for cylindrical geom
            pass  # in this case, theta unit is dimensionless
        else:
            value = yt.YTQuantity(value, oldUnit).to_value(newUnit)
        if key in ["HorWidth", "VerWidth"] and value == 0.0:
            Edit_Dict[key].setText("")
            try:
                Param_Dict[key] = Param_Dict[key.replace("W", "DomainW")].to_value(newUnit)
            except AttributeError:
                GUILogger.debug("Width couldn't be set")
                pass  # this sometimes happens when restoring the parameter dict
        else:
            Edit_Dict[key].setText("{0:.3g}".format(value))
    if mode == "Grid":
        if not Param_Dict["isValidFile"]:
            return
        try:
            maxHor = Param_Dict["HorDomainWidth"].to_value(newUnit)
            maxVer = Param_Dict["VerDomainWidth"].to_value(newUnit)
            Edit_Dict["HorWidth"].setToolTip("Set the horizontal width to a value "
                                             f"between 0 and {maxHor:.3g} {newUnit}.")
            Edit_Dict["VerWidth"].setToolTip("Set the vertical width to a value "
                                             f"between 0 and {maxVer:.3g} {newUnit}.")
            ds = Param_Dict["CurrentDataSet"]
            for axis, field in zip(["X", "Y", "Z"], Param_Dict["XFields"][:3]):  # i.e. r, z, theta
                minVal = Param_Dict["FieldMins"][field]
                maxVal = Param_Dict["FieldMaxs"][field]
                unit = Param_Dict["FieldUnits"][field]
                if field != "theta":
                    minVal = yt.YTQuantity(ds.quan(minVal, unit)).to_value(newUnit)
                    maxVal = yt.YTQuantity(ds.quan(maxVal, unit)).to_value(newUnit)
                else:
                    newUnit = ""
                Edit_Dict[axis + "Center"].setToolTip(
f"Set the central {field}-coordinate to a value between {minVal:.3g} {newUnit} and {maxVal:.3g} {newUnit}")
        except (KeyError) as e:
            GUILogger.debug(e)


def getFloatInput(Param_Dict, Edit_Dict, axis, mode):
    """Reads out the text of the lineedits and stores them in Param_Dict.
    Parameters:
        Param_Dict: Parameter Dictionary
        LineEdit: LineEdit that the text is read of
        axis: "X", "Y", "Z"
        mode: "LStart" and "LEnd", "NormDir", "NormNorth"
    """
    try:
        Param_Dict[axis + mode] = float(Edit_Dict[axis + mode].text())
        Edit_Dict[axis + mode].turnTextBlack()
    except ValueError:
        Param_Dict[axis + mode] = 0.0
        Edit_Dict[axis + mode].turnTextRed()
    if mode in ["NormNorth", "NormDir"]:
        normVec = [Param_Dict[axis_ + "NormDir"] for axis_ in ["X", "Y", "Z"]]
        northVec = [Param_Dict[axis_ + "NormNorth"] for axis_ in ["X", "Y", "Z"]]
#        GUILogger.debug(normVec, northVec)
        if normVec == northVec:
            GUILogger.warning("The normal vector can't be the same as the north "
                              "vector. I've changed the north vector for you.")
            Edit_Dict[axis + "NormNorth"].setText(str(Param_Dict[axis + "NormNorth"]+1.))


def setLineLengthLabel(Param_Dict, Label_Dict):
    """Calculate the current length of the line and set the label properly."""
    means = [(Param_Dict[axis+"LStart"]-Param_Dict[axis+"LEnd"])**2
             for axis in ["X", "Y", "Z"]]
    length = sum(means)**0.5
    unit = Param_Dict["LineUnit"]
    Label_Dict["LineLength"].setText(f"Line length: {length:.3g} {unit}")


def getCenterInput(Param_Dict, Edit_Dict, axis):
    """Reads out current center coordinates and gives appropriate feedback"""
    lineEdit = Edit_Dict[axis + "Center"]
    field = Param_Dict["XFields"][["X", "Y", "Z"].index(axis)]  # i.e. r, z or theta
    if not Param_Dict["isValidFile"]:
        lineEdit.turnTextBlue()
        return
    try:
        inputNumber = float(lineEdit.text())
        unit = Param_Dict["GridUnit"]
        ds = Param_Dict["CurrentDataSet"]
        minVal = Param_Dict["FieldMins"][field]
        maxVal = Param_Dict["FieldMaxs"][field]
        fieldUnit = Param_Dict["FieldUnits"][field]
        if field != "theta":
            minVal = yt.YTQuantity(ds.quan(minVal, fieldUnit)).to_value(unit)
            maxVal = yt.YTQuantity(ds.quan(maxVal, fieldUnit)).to_value(unit)
        else:
            unit = ""
        minVal = float(f"{minVal:.3g}")  # round them so they're comparable
        maxVal = float(f"{maxVal:.3g}")
        if (inputNumber >= minVal) and (inputNumber <= maxVal):
            lineEdit.turnTextBlack()
        else:
            lineEdit.turnTextRed()
    except (ValueError, KeyError):
        lineEdit.turnTextRed()
        inputNumber = 0.0
    Param_Dict[axis + "Center"] = inputNumber


def getTextInput(Param_Dict, Edit_Dict, key):
    """Reads out current text of the lineEdit corresponding to key and saves it
    in Param_Dict"""
    text = Edit_Dict[key].text()
    if key == "Zoom":
        try:
            text = float(text)
        except ValueError:
            text = 1
        if text != 1:
            GUILogger.warning("Setting the zoom to a value not equal to 1 might interfere with setting the width.")
    Param_Dict[key] = text


def getColorInput(Param_Dict, Edit_Dict):
    """Reads out the text of the color scheme edit and gives visual feedback on
    its validity."""
    lineEdit = Edit_Dict["ColorScheme"]
    if lineEdit.text() not in validColors:
        lineEdit.turnTextRed()
        Param_Dict["ColorScheme"] = config["Misc"]["colorscheme"]
    else:
        lineEdit.turnTextBlack()
        Param_Dict["ColorScheme"] = lineEdit.text()


def getWidthInput(Param_Dict, Edit_Dict, orientation):
    """Reads out the text of the with edits and gives visual feedback on its
    validity.
    Parameters:
        Param_Dict: For the maximum widths and units
        Edit_Dict: To access hor or vert LineEdits
        orientation: "Hor" or "Ver" for horizontal or vertical
    """
    lineEdit = Edit_Dict[orientation + "Width"]
    if not Param_Dict["isValidFile"]:
        lineEdit.turnTextBlue()
        return
    # Upon choosing a normal vector, the constraints are already saved as
    # YTQuantities in the parameter dictionary:
    unit = Param_Dict["GridUnit"]
    maxWidth = Param_Dict[orientation + "DomainWidth"]
    maxWidth = maxWidth.to_value(unit)
    offAxis = (Param_Dict["NormVecMode"] == "Off-Axis")
    try:
        inputNumber = float(lineEdit.text())
        maxWidth = float(f"{maxWidth:.3g}")  # round so they're comparable
        if offAxis or 0 < inputNumber <= maxWidth:  # The validator should prevent neg. values anyways
            lineEdit.turnTextBlack()
        else:
            lineEdit.turnTextRed()
    except (ValueError, KeyError):
        if lineEdit.text() == "":
            lineEdit.turnTextBlack()
        else:
            lineEdit.turnTextRed()  # not sure when this could happen
        inputNumber = maxWidth
    Param_Dict[orientation + "Width"] = inputNumber
#    GUILogger.debug(f"Set the {orientation} width to {inputNumber}")


# %% CheckBox-related stuff
def getAnnotationInput(Param_Dict, CheckBox_Dict, key):
    """Connect the output of the Checkboxes to their corresponding entry in the
    parameter dictionary."""
    Param_Dict[key] = CheckBox_Dict[key].isChecked()


def freezeNormVecMode(Param_Dict, RadioDict_Dict):
    """Whenever particle plot is chosen, freeze the options for choosing a
    custom normal vector"""
    particle = Param_Dict["ParticlePlot"]
    RadioDict_Dict["NormVecMode"]["Off-Axis"].setDisabled(particle)
    if particle:
        RadioDict_Dict["NormVecMode"]["Axis-Aligned"].setChecked(True)
        GUILogger.warning("Particle plots are still an experimental feature "
                          "and might produce errors!")
        if Param_Dict["PlotMode"] == "Projection" and Param_Dict["Geometry"] == "cartesian":
            GUILogger.log(29, "Disabled off-axis-projections since they are "
                          "not supported for particle plots.")


def freezeXAxis(Param_Dict, CheckBox_Dict, ComboBox_Dict, Edit_Dict,
                Button_Dict):
    """Freeze the x-Axis so the settings from the last profile plot are kept,
    or unfreeze it."""
    if Param_Dict["AddProfile"] and Param_Dict["PlotMode"] == "Profile":
        PlotWindow = Param_Dict["CurrentPlotWindow"]
        try:
            PW_Dict = PlotWindow.Param_Dict
            CheckBox_Dict["XLog"].setChecked(PW_Dict["XLog"])
            ComboBox_Dict["XAxis"].setCurrentText(PW_Dict["XAxis"])
            Edit_Dict["XUnit"].setText(PW_Dict["XUnit"])
            for key in ["Min", "Max"]:
                Edit_Dict["X" + key].setText("{:.3g}".format(PW_Dict["X" + key]))
            freeze = True
        except AttributeError:
            freeze = False
    else:
        freeze = False
    CheckBox_Dict["XLog"].setDisabled(freeze)
    ComboBox_Dict["XAxis"].setDisabled(freeze)
    for key in ["Unit", "Min", "Max"]:
        Edit_Dict["X" + key].setDisabled(freeze)
    Button_Dict["XCalc"].setDisabled(freeze)


# %% RadioButton-related stuff
def changeEvalMode(Param_Dict, RadioDict_Dict):
    """Reads out current Evaluation Mode and stores it in Param_Dict.
    Parameters:
        Param_Dict: Parameter dictionary for storing information
        RadioDict_Dict: RadioButton Dictionary for checking evaluation status
    returns:
        change: bool: True if change has occured, false otherwise.
    """
    oldMode = Param_Dict["EvalMode"]
    Eval_Dict = RadioDict_Dict["EvalMode"]
    if Eval_Dict["Single file"].isChecked():
        Param_Dict["EvalMode"] = "Single"
    elif Eval_Dict["Time series"].isChecked():
        Param_Dict["EvalMode"] = "Series"
    return Param_Dict["EvalMode"] != oldMode


def changeOpenButton(Param_Dict, Button_Dict, Status_Dict, Wid_Dict):
    """Changes the text and tooltip of the OpenF-Button and the availability
    of certain buttons depending on selected mode. Also update status.
    Parameters:
        Param_Dict: Parameter Dictionary for storing information
        Button_Dict: Button Dictionary for changing the openFileButton
        Status_Dict: Status dictionary for updating file status
    """
    openButton = Button_Dict["Open"]
    if Param_Dict["EvalMode"] == "Single":
        enablePlotOptions(Wid_Dict, Button_Dict, Param_Dict["isValidFile"])
        Button_Dict["PlotAll"].setHidden(True)
        openButton.setText('Open file')
        openButton.setToolTip("Open a new file to analyze [Ctrl+O]")
        if Param_Dict["isValidFile"]:
            openButton.makeTextBold()
        else:
            openButton.makeButtonRed()
            Status_Dict["Status"].setText("Click 'Open file' to start.")
    elif Param_Dict["EvalMode"] == "Series":
        openButton.setText('Open directory')
        openButton.setToolTip("Open a directory to analyze time series [Ctrl+D]")
        enablePlotOptions(Wid_Dict, Button_Dict, Param_Dict["isValidSeries"])
        Button_Dict["PlotAll"].setHidden(False)
        if Param_Dict["isValidSeries"]:
            openButton.makeTextBold()
        else:
            openButton.makeButtonRed()
            Status_Dict["Status"].setText("Click 'Open directory' to start.")


def enablePlotOptions(Wid_Dict, Button_Dict, enabled=True):
    """Disables all widgets relevant for plotting"""
    widKeys = ["NormVecMode", "XAxis", "YAxis", "ZAxis", "NAxis",
               "SlcProjOptions", "LineOptions", "ProfileOptions",
               "ParticlePlot"]
    for key in widKeys:
        Wid_Dict[key].setEnabled(enabled)
    butKeys = ["WriteScript", "AddDerField", "Evaluate", "PlotAll"]
    for key in butKeys:
        Button_Dict[key].setEnabled(enabled)


def getDimensionInput(Param_Dict, RadioDict_Dict):
    """When 1D or 2D is pressed, save parameters of the mode"""
    if RadioDict_Dict["DimMode"]["1D"].isChecked():
        Param_Dict["DimMode"] = "1D"
    else:
        Param_Dict["DimMode"] = "2D"


def changeDimensions(Param_Dict, Wid_Dict):
    """Hides/shows 1D/2D Plot options"""
    if Param_Dict["DimMode"] == "1D":
        Wid_Dict["2DOptions"].setHidden(True)
        Wid_Dict["1DOptions"].setHidden(False)
    elif Param_Dict["DimMode"] == "2D":
        Wid_Dict["2DOptions"].setHidden(False)
        Wid_Dict["1DOptions"].setHidden(True)


def getPlotModeInput(Param_Dict, RadioDict_Dict):
    """When 1DMode or 2DMode is changed, toggle display of mode and save params
    Parameters:
        Param_Dict: Where PlotMode is stored
    """
    if Param_Dict["DimMode"] == "1D":
        if RadioDict_Dict["1DOptions"]["Profile"].isChecked():
            newMode = "Profile"
        elif RadioDict_Dict["1DOptions"]["Line"].isChecked():
            newMode = "Line"
    elif Param_Dict["DimMode"] == "2D":
        if RadioDict_Dict["2DOptions"]["Phase"].isChecked():
            newMode = "Phase"
        elif RadioDict_Dict["2DOptions"]["Slice"].isChecked():
            newMode = "Slice"
        elif RadioDict_Dict["2DOptions"]["Projection"].isChecked():
            newMode = "Projection"
    Param_Dict["PlotMode"] = newMode


def getNormVecModeInput(Param_Dict, RadioDict_Dict):
    """Reads out the Radiobuttons concerning the normal vector mode and stores
    it.
    Parameters:
        Param_Dict: Parameter Dictionary
        RadioDict_Dict: Dictionary with the buttons for NormVecMode
    """
    if RadioDict_Dict["NormVecMode"]["Off-Axis"].isChecked():
        oldMode = Param_Dict["NormVecMode"]
        newMode = "Off-Axis"
        if oldMode != newMode:
            if Param_Dict["isValidFile"] and Param_Dict["Geometry"] == "cylindrical":
                GUILogger.warning("yt doesn't like off-axis slices and project"
                                  "ions in cylindrical geometry, so <b>errors "
                                  "might occur.</b>")
    else:
        newMode = "Axis-Aligned"
    Param_Dict["NormVecMode"] = newMode


def prepareForNormVec(Param_Dict, ComboBox_Dict, Wid_Dict, CheckBox_Dict,
                      Edit_Dict):
    """Enables and disables some widgets according to the current normvec mode.
    """
    aligned = Param_Dict["NormVecMode"] == "Axis-Aligned"
    Wid_Dict["NAxis"].layout().itemAt(1).widget().setVisible(aligned) # ComboBox
    for i in range(2, 6):  # Labels and LineEdits
        Wid_Dict["NAxis"].layout().itemAt(i).widget().setHidden(aligned)
    if Param_Dict["PlotMode"] == "Projection":
        CheckBox_Dict["DomainDiv"].setVisible(aligned)
    if aligned and Param_Dict["isValidFile"]:
        getDomainConstraints(Param_Dict, Edit_Dict)
    else:
        Edit_Dict["HorWidth"].setToolTip("Set the horizontal width")
        Edit_Dict["VerWidth"].setToolTip("Set the vertical width")


# %% Layout-related stuff
def changeToPhase(Param_Dict, Wid_Dict, CheckBox_Dict, ComboBox_Dict,
                  Edit_Dict, Button_Dict):
    """Constructs the options menu for Phase Plot"""
    Wid_Dict["LineOptions"].setHidden(True)
    Wid_Dict["XAxis"].setHidden(False)
    Wid_Dict["YAxis"].setHidden(False)
    Wid_Dict["ZAxis"].setHidden(False)
    Wid_Dict["NAxis"].setHidden(True)
    Wid_Dict["SlcProjOptions"].setHidden(True)
    Wid_Dict["ProfileOptions"].setHidden(True)
    Wid_Dict["ParticlePlot"].setHidden(False)
    if Param_Dict["isValidFile"]:
        Wid_Dict["ParticlePlot"].setEnabled(True)
    if ComboBox_Dict["XAxis"].findText("time") == 0:
        ComboBox_Dict["XAxis"].removeItem(0)
    if Param_Dict["WeightField"] is None:
        ComboBox_Dict["ZWeight"].setCurrentText('None')
    else:
        ComboBox_Dict["ZWeight"].setCurrentText(Param_Dict["WeightField"])
    checkBoxKeys = ["Scale", "Grid", "VelVectors",
                    "VelStreamlines", "MagVectors", "MagStreamlines",
                    "Contour", "ParticleAnno", "LineAnno"]
    for key in checkBoxKeys:
        CheckBox_Dict[key].hide()
    Edit_Dict["PSlabWidth"].setHidden(True)
    slay.hideShowLabels(Wid_Dict["ZAxis"].layout(), 10, 11, False)  # Show 'WeightField'
    slay.hideShowLabels(Wid_Dict["ZAxis"].layout(), 14, 15, True)  # Hide 'DomainDiv'
    Button_Dict["PlotHelp2D"].setToHelp("phase plots")


def changeToProjection(Param_Dict, Wid_Dict, CheckBox_Dict, ComboBox_Dict,
                       Button_Dict, Edit_Dict):
    """Constructs the options menu for Projection"""
    Wid_Dict["LineOptions"].setHidden(True)
    Wid_Dict["XAxis"].setHidden(True)
    Wid_Dict["YAxis"].setHidden(True)
    Wid_Dict["ZAxis"].setHidden(False)
    Wid_Dict["NAxis"].setHidden(False)
    Wid_Dict["SlcProjOptions"].setHidden(False)
    Wid_Dict["SlcProjOptions"].setTitle("Projection plot options")
    Wid_Dict["ProfileOptions"].setHidden(True)
    Wid_Dict["ParticlePlot"].setHidden(False)
    if Param_Dict["Geometry"] == "cartesian" and Param_Dict["isValidFile"]:
        Wid_Dict["ParticlePlot"].setEnabled(True)
    else:
        Wid_Dict["ParticlePlot"].setDisabled(True)
        CheckBox_Dict["ParticlePlot"].setChecked(False)
    try:
        plotType = Param_Dict["CurrentPlotWindow"].Param_Dict["isValidPlot"]
        geometry = Param_Dict["CurrentPlotWindow"].Param_Dict["Geometry"]
        normVecMode = Param_Dict["CurrentPlotWindow"].Param_Dict["NormVecMode"]
        if geometry == "cartesian" and plotType in ["Slice", "Projection"] and normVecMode == "Axis-Aligned":
            Button_Dict["MakeLinePlot"].show()
        else:
            Button_Dict["MakeLinePlot"].hide()
    except AttributeError:
        Button_Dict["MakeLinePlot"].hide()
    if ComboBox_Dict["XAxis"].findText("time") == 0:
        ComboBox_Dict["XAxis"].removeItem(0)
    if Param_Dict["WeightField"] is None:
        ComboBox_Dict["ZWeight"].setCurrentText("None")
    else:
        ComboBox_Dict["ZWeight"].setCurrentText(Param_Dict["WeightField"])
    if Param_Dict["Geometry"] == "cartesian":
        checkBoxKeys = ["Scale", "VelVectors", "VelStreamlines",
                        "MagVectors", "MagStreamlines", "Contour",
                        "ParticleAnno"]
        for key in checkBoxKeys:
            CheckBox_Dict[key].show()
        Edit_Dict["PSlabWidth"].setHidden(False)
    CheckBox_Dict["Grid"].show()
    CheckBox_Dict["LineAnno"].hide()
    slay.hideShowLabels(Wid_Dict["ZAxis"].layout(), 10, 11, False)  # Show 'WeightField'
    if Param_Dict["NormVecMode"] == "Axis-Aligned":
        slay.hideShowLabels(Wid_Dict["ZAxis"].layout(), 14, 15, False)  # Show 'DomainDiv'
    Button_Dict["PlotHelp2D"].setToHelp("projection plots")


def changeToSlice(Param_Dict, Wid_Dict, CheckBox_Dict, ComboBox_Dict,
                  Button_Dict, Edit_Dict):
    """Constructs the options menu for Slicing"""
    Wid_Dict["LineOptions"].setHidden(True)
    Wid_Dict["XAxis"].setHidden(True)
    Wid_Dict["YAxis"].setHidden(True)
    Wid_Dict["ZAxis"].setHidden(False)
    Wid_Dict["NAxis"].setHidden(False)
    Wid_Dict["SlcProjOptions"].setHidden(False)
    Wid_Dict["SlcProjOptions"].setTitle("Slice plot options")
    Wid_Dict["ProfileOptions"].setHidden(True)
    Wid_Dict["ParticlePlot"].setHidden(True)
    CheckBox_Dict["ParticlePlot"].setChecked(False)
    try:
        plotType = Param_Dict["CurrentPlotWindow"].Param_Dict["isValidPlot"]
        geometry = Param_Dict["CurrentPlotWindow"].Param_Dict["Geometry"]
        normVecMode = Param_Dict["CurrentPlotWindow"].Param_Dict["NormVecMode"]
        if geometry == "cartesian" and plotType in ["Slice", "Projection"] and normVecMode == "Axis-Aligned":
            Button_Dict["MakeLinePlot"].show()
        else:
            Button_Dict["MakeLinePlot"].hide()
    except AttributeError:
        Button_Dict["MakeLinePlot"].hide()
    if ComboBox_Dict["XAxis"].findText("time") == 0:
        ComboBox_Dict["XAxis"].removeItem(0)
    if Param_Dict["Geometry"] == "cartesian":
        checkBoxKeys = ["Scale", "VelVectors", "VelStreamlines",
                        "MagVectors", "MagStreamlines", "Contour",
                        "ParticleAnno"]
        for key in checkBoxKeys:
            CheckBox_Dict[key].show()
        Edit_Dict["PSlabWidth"].setHidden(False)
    CheckBox_Dict["Grid"].show()
    CheckBox_Dict["LineAnno"].hide()
    slay.hideShowLabels(Wid_Dict["ZAxis"].layout(), 10, 11, True)  # Hide 'WeightField'
    slay.hideShowLabels(Wid_Dict["ZAxis"].layout(), 14, 15, True)  # Hide 'DomainDiv'
    Button_Dict["PlotHelp2D"].setToHelp("slice plots")


def changeToLine(Param_Dict, Wid_Dict, CheckBox_Dict, Edit_Dict, Button_Dict):
    """Constructs the options menu for Line Plot"""
    Wid_Dict["LineOptions"].setHidden(False)
    Wid_Dict["XAxis"].setHidden(True)
    Wid_Dict["YAxis"].setHidden(False)
    Wid_Dict["ZAxis"].setHidden(True)
    Wid_Dict["NAxis"].setHidden(True)
    Wid_Dict["SlcProjOptions"].setHidden(True)
    Wid_Dict["ProfileOptions"].setHidden(True)
    Wid_Dict["ParticlePlot"].setHidden(True)
    CheckBox_Dict["ParticlePlot"].setChecked(False)
    checkBoxKeys = ["Scale", "Grid", "VelVectors",
                    "VelStreamlines", "MagVectors", "MagStreamlines",
                    "Contour", "ParticleAnno"]
    for key in checkBoxKeys:
        CheckBox_Dict[key].hide()
    CheckBox_Dict["LineAnno"].show()
    Edit_Dict["PSlabWidth"].setHidden(True)
    Button_Dict["PlotHelp1D"].setToHelp("line plots")


def changeToProfile(Param_Dict, Wid_Dict, CheckBox_Dict, ComboBox_Dict,
                    Misc_Dict, Edit_Dict, Button_Dict):
    """Constructs the options menu for Profile Plot"""
    Wid_Dict["LineOptions"].setHidden(True)
    Wid_Dict["XAxis"].setHidden(False)
    Wid_Dict["YAxis"].setHidden(False)
    Wid_Dict["ZAxis"].setHidden(True)
    Wid_Dict["NAxis"].setHidden(True)
    Wid_Dict["SlcProjOptions"].setHidden(True)
    Wid_Dict["ProfileOptions"].setHidden(False)
    Wid_Dict["ParticlePlot"].setHidden(True)
    CheckBox_Dict["ParticlePlot"].setChecked(False)
    # Enable the option to add a second profile plot
    if not Param_Dict["CurrentPlotWindow"].hasProfile:
        CheckBox_Dict["AddProfile"].setChecked(False)
    CheckBox_Dict["AddProfile"].setEnabled(Param_Dict["CurrentPlotWindow"].hasProfile)
    CheckBox_Dict["TimeSeriesProf"].setHidden(not Param_Dict["isValidSeries"])
    Misc_Dict["ProfileSpinner"].setHidden(not Param_Dict["isValidSeries"])
    timeIndex = ComboBox_Dict["XAxis"].findText("time")
    if Param_Dict["EvalMode"] == "Series" and timeIndex == -1:
        ComboBox_Dict["XAxis"].insertItem(0, "time")
    elif Param_Dict["EvalMode"] == "Single" and timeIndex != -1:
        ComboBox_Dict["XAxis"].removeItem(timeIndex)
    if Param_Dict["WeightField"] is None:
        ComboBox_Dict["YWeight"].setCurrentText('None')
    else:
        ComboBox_Dict["YWeight"].setCurrentText(Param_Dict["WeightField"])
    checkBoxKeys = ["Scale", "Grid", "VelVectors",
                    "VelStreamlines", "MagVectors", "MagStreamlines",
                    "Contour", "ParticleAnno", "LineAnno"]
    for key in checkBoxKeys:
            CheckBox_Dict[key].hide()
    Edit_Dict["PSlabWidth"].setHidden(True)
    Button_Dict["PlotHelp1D"].setToHelp("profile plots")


def updateLabels(Param_Dict, Label_Dict):
    """Scans the dataset for its time and updates the label."""
    if Param_Dict["isValidSeries"] and Param_Dict["EvalMode"] == "Series":
        ds = Param_Dict["CurrentDataSet"]
        Label_Dict["Dimensions"].setText("Dim: " + str(ds.dimensionality) + "D")
        Label_Dict["Geometry"].setText(str(ds.geometry).capitalize() + " geometry")
    elif Param_Dict["isValidFile"] and Param_Dict["EvalMode"] == "Single":
        ds = Param_Dict["CurrentDataSet"]
        time = ds.current_time
        time = time.convert_to_units("kyr")
        Param_Dict["DataSetTime"] = time
        Label_Dict["CurrentDataSet"].setText("{}: ".format(ds))
        timeString = "{:.3g} ".format(time.value)
        timeString += str(time.units)
        Label_Dict["DataSetTime"].setText(timeString)
        Label_Dict["Dimensions"].setText("Dim: " + str(ds.dimensionality) + "D")
        Label_Dict["Geometry"].setText(str(ds.geometry).capitalize() + " geometry")
    else:
        Label_Dict["CurrentDataSet"].setText("")
        Label_Dict["DataSetTime"].setText("")
        Label_Dict["Dimensions"].setText("")
        Label_Dict["Geometry"].setText("")


def fillDataSetDict(Param_Dict, Status_Dict, TopLayout, _main):
    """Scans the current DataSeries object for the times of the datasets,
    stores them in the DataSetDict and also creates PlotWindows"""
    length = len(Param_Dict["DataSeries"])
    for i, ds in enumerate(Param_Dict["DataSeries"]):
        time = ds.current_time
        Param_Dict["DataSetDict"][str(ds) + "Time"] = time.convert_to_units("kyr")
        # Initialize a plot window for each dataset so we can have individual plots
        Window = PlotWindow(Status_Dict, parent=_main)
        Window.hide()
        TopLayout.addWidget(Window, 0, 0)
        Param_Dict["DataSetDict"][str(ds) + "PlotWindow"] = Window
        if i % ceil(length/4) == 0:  # This way, at max 4 updates are printed
            GUILogger.info(f"Loading dataset {i+1}/{length}...")
    Param_Dict["FieldMins"]["time"] = Param_Dict["DataSetDict"][str(Param_Dict["DataSeries"][0]) + "Time"]
    Param_Dict["FieldMaxs"]["time"] = Param_Dict["DataSetDict"][str(Param_Dict["DataSeries"][-1]) + "Time"]


def getProfOfEveryInput(Param_Dict, Misc_Dict):
    """Stores the input given for the spinner box in the param_Dict."""
    Param_Dict["ProfOfEvery"] = Misc_Dict["ProfileSpinner"].value()


def getSliderInput(Param_Dict, Label_Dict, Misc_Dict, value=None,
                   seriesEval=False):
    """Reads out the current slider value, sets the dataset and the status
    information (name and time) on screen.
    Parameters:
        Param_Dict: For DataSeries, DataSet and DataSetDict"""
    if value is None:
        value = Misc_Dict["SeriesSlider"].value()
    ds = Param_Dict["DataSeries"][value]
    Param_Dict["CurrentPlotWindow"].hide()
    Param_Dict["CurrentPlotWindow"] = Param_Dict["DataSetDict"][str(ds) + "PlotWindow"]
    Param_Dict["CurrentPlotWindow"].show()
    Label_Dict["CurrentDataSet"].setText("{}: ".format(ds))
    time = Param_Dict["DataSetDict"][str(ds) + "Time"]
    timeString = "{:.3g} ".format(time.value)
    timeString += str(time.units)
    Label_Dict["DataSetTime"].setText(timeString)
    Param_Dict["CurrentDataSet"] = ds
    if not seriesEval:
        GUILogger.info(f"Selected the file '{str(ds)}' at {timeString}.")
    else:
        GUILogger.debug(f"Selected the file '{str(ds)}' at {timeString}.")


def restoreFromParam_Dict(Param_Dict, CheckBox_Dict, ComboBox_Dict, Edit_Dict,
                          Label_Dict, RadioDict_Dict, Button_Dict, Misc_Dict,
                          Wid_Dict):
    """Takes a given Param_Dict of a plot window and sets the widgets in the
    window accordingly."""
    # CheckBox_Dict:
    checkBoxKeys = ["Timestamp", "Scale", "Grid", "VelVectors",
                    "VelStreamlines", "MagVectors", "MagStreamlines",
                    "Contour", "XLog", "YLog", "ZLog",
                    "DomainDiv", "TimeSeriesProf",
                    "ParticleAnno", "LineAnno", "SetAspect"]
    for key in checkBoxKeys:
        CheckBox_Dict[key].setChecked(Param_Dict[key])
    # ComboBox_Dict:
    updateNormalAxis(Param_Dict, ComboBox_Dict)
    updateComboBoxes(Param_Dict, ComboBox_Dict)
    comboBoxKeys = ["TimeQuantity", "XAxis", "YAxis", "ZAxis", "NAxis"]
    for key in comboBoxKeys:  # TimeQuantity needs to be called before XAxis
        field = Param_Dict[key]
        ComboBox_Dict[key].setCurrentText(field)
    wfield = Param_Dict["WeightField"]
    ComboBox_Dict["YWeight"].setCurrentText(wfield)
    ComboBox_Dict["ZWeight"].setCurrentText(wfield)
    # LineEdit_Dict: Treat Floats and Strings differently
    lineEditKeys = ["XUnit", "YUnit", "ZUnit", "LineUnit", "GridUnit",
                     "PlotTitle", "ColorScheme"]
    for key in lineEditKeys:
        Edit_Dict[key].setText(str(Param_Dict[key]))
    lineEditKeys = ["XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax",
                    "XLStart", "YLStart", "ZLStart",
                    "XLEnd", "YLEnd", "ZLEnd",
                    "XCenter", "YCenter", "ZCenter", "HorWidth", "VerWidth"]
    for key in lineEditKeys:
        if Param_Dict[key] == "":
            Edit_Dict[key].setText(Param_Dict[key])
        else:
            Edit_Dict[key].setText("{0:.3g}".format(Param_Dict[key]))
    Edit_Dict["Zoom"].setText(str(Param_Dict["Zoom"]))
    # Label_Dict:
    labelKeys = ["XMinUnit", "YMinUnit", "ZMinUnit", "XMaxUnit", "YMaxUnit",
                 "ZMaxUnit",
                 "XCenUnit", "YCenUnit", "ZCenUnit", "HorWidthUnit",
                 "VerWidthUnit",
                 "CurrentDataSet", "DataSetTime", "Geometry"]
    labelParamKeys = ["XUnit", "YUnit", "ZUnit", "XUnit", "YUnit",
                      "ZUnit", "GridUnit", "GridUnit", "GridUnit",
                      "GridUnit", "GridUnit",
                      "CurrentDataSet", "DataSetTime", "Geometry"]
    for lkey, pkey in zip(labelKeys, labelParamKeys):
        Label_Dict[lkey].setText(str(Param_Dict[pkey]))
    Label_Dict["Dimensions"].setText("")
    updateLabels(Param_Dict, Label_Dict)
    # RadioDict_Dict (we need to do some case checking here since I used
    # different key words in Param_Dict:
    if Param_Dict["EvalMode"] == "Single":
        RadioDict_Dict["EvalMode"]["Single file"].setChecked(True)
        Misc_Dict["SeriesSlider"].hide()
        Param_Dict["CurrentPlotWindow"] = Param_Dict["DataSetPlotWindow"]
        if Param_Dict["isValidFile"]:
            ds = Param_Dict["CurrentDataSet"]
            time = Param_Dict["DataSetTime"]
            timeString = "{:.3g} ".format(time.value)
            timeString += str(time.units)
            GUILogger.info("Selected the file '{}' at {}.".format(str(ds), timeString))
    else:
        RadioDict_Dict["EvalMode"]["Time series"].setChecked(True)
        if Param_Dict["isValidSeries"]:
            slider = Misc_Dict["SeriesSlider"]
            length = len(Param_Dict["DataSeries"])
            slider.setRange(0, length-1)
            slider.setValue(findIndex(Param_Dict))
            slider.show()
            spinner = Misc_Dict["ProfileSpinner"]
            spinner.setMaximum(length)
            spinner.setValue(Param_Dict["ProfOfEvery"])
            spinner.setDisabled(False)
            # this will set the currentPlotWindow. We can't call the signal
            # handler because it still holds the old Param_Dict.
            getSliderInput(Param_Dict, Label_Dict, Misc_Dict)
            Param_Dict["isValidFile"] = True
        else:
            Param_Dict["isValidFile"] = False
    Param_Dict["CurrentPlotWindow"].show()
    if Param_Dict["PlotMode"] == "Line":
        RadioDict_Dict["1DOptions"]["Line"].setChecked(True)
    if Param_Dict["PlotMode"] == "Profile":
        RadioDict_Dict["1DOptions"]["Profile"].setChecked(True)
    if Param_Dict["PlotMode"] == "Phase":
        RadioDict_Dict["2DOptions"]["Phase"].setChecked(True)
    if Param_Dict["PlotMode"] == "Slice":
        RadioDict_Dict["2DOptions"]["Slice"].setChecked(True)
    if Param_Dict["PlotMode"] == "Projection":
        RadioDict_Dict["2DOptions"]["Projection"].setChecked(True)
    radioKeys = ["NormVecMode", "DimMode"]
    for key in radioKeys:
        RadioDict_Dict[key][Param_Dict[key]].setChecked(True)
    # Set Placeholders and Tooltips etc.:
    for axis in ["X", "Y", "Z"]:
        Button_Dict[axis + "Calc"].setHidden(not Param_Dict["isValidFile"])
        if Param_Dict["isValidFile"]:
            checkCalculated(Param_Dict, Button_Dict, Edit_Dict,
                            axis, ComboBox_Dict, CheckBox_Dict)
        else:
            Edit_Dict[axis + "Min"].setPlaceholderText("default")
            Edit_Dict[axis + "Min"].setToolTip("Press 'Calculate Extrema' to"
                                               "get Extrema for this field.")
            Edit_Dict[axis + "Max"].setPlaceholderText("default")
            Edit_Dict[axis + "Max"].setToolTip("Press 'Calculate Extrema' to"
                                               "get Extrema for this field.")
        field = Param_Dict[axis + "Axis"]
        fieldUnit = Param_Dict["FieldUnits"][field]
        Edit_Dict[axis + "Unit"].setPlaceholderText(str(fieldUnit))
        Edit_Dict[axis + "Unit"].setToolTip("Set unit of this field to " +
                                            str(fieldUnit.dimensions) +
                                            "-dimension")
    ComboBox_Dict["XAxis"].setCurrentText(Param_Dict["XAxis"])  # in case we have a time series
    # Because the logbox is resized, it can happen that it is scrolled up.
    if not Param_Dict["TestingMode"]:
        Misc_Dict["LogBox"].moveCursor(QG.QTextCursor.End)
