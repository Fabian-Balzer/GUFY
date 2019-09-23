# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Contains a collection of convenience functions used, especially for
handling startup, plot manipulation and miscellaneous.

The module is structured as follows:
    - General helper functions
    - Helper functions for plotting, including annotations and extrema calc
    - Functions needed for threading
    - Functions for setting up a file/series
    - Functions for line drawing
"""


from datetime import datetime
from math import ceil
from os import mkdir
import yt
from PyQt5.Qt import PYQT_VERSION_STR as PyQtVersion
from matplotlib import __version__ as mplVersion
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
import PyQt5.QtWidgets as QW
from simgui_modules.logging import GUILogger


# %% General helper functions
def alertUser(text, title="Something went wrong"):
    Alert = QW.QMessageBox()
    Alert.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
    Alert.setIcon(QW.QMessageBox.Warning)
    Alert.setWindowTitle(title)
    Alert.setText(text)
    Alert.exec()


def checkVersions():
    """Helper function to determine whether the versions of yt, pyqt and mpl
    the user has installed are sufficient for a smooth run."""
    errorString = "It seems that you do not have the required modules \
        installed.\n"
    ytNums = yt.__version__.split(".")
    ytCheck = float(ytNums[0]) >= 3 and float(ytNums[1]) >= 5
    if not ytCheck:
        errorString += (f"Your version of the yt-module is {yt.__version__}, "
                        "but you need v. 3.5 or later\n")
    PyQtNums = PyQtVersion.split(".")
    PyQtCheck = float(PyQtNums[0]) >= 5 and float(PyQtNums[1]) >= 9
    if not PyQtCheck:
        errorString += (f"Your version of the PyQt-module is {PyQtVersion}, "
                        "but you need v. 5.9 or later\n")
    mplNums = mplVersion.split(".")
    mplCheck = float(mplNums[0]) >= 3
    if not mplCheck:
        errorString += (f"Your version of the matplotlib-module is "
                        f"{mplVersion}, but you need v. 3.0 or later\n")
    if not (ytCheck and PyQtCheck and mplCheck):
        raise RuntimeError(errorString)


def convertToLessThanThree(number):
    """Converts and returns a given number number to a value between 0 and 2"""
    if number > 2:
        return number - 3
    else:
        return number


def findIndex(Param_Dict):
    """Convenience method to find the index of a dataset in the dataset series.
    Unfortunately there seems to be no easier way.
    Returns:
        index: int: index of the current dataset in the series"""
    nameList = [str(ds) for ds in Param_Dict["DataSeries"]]
    index = nameList.index(str(Param_Dict["CurrentDataSet"]))
    return index


def mean(xs):
    """Compute and return the average of all entries in a given list xs"""
    if len(xs) == 0:
        return 0
    return sum(xs)/len(xs)


def refreshWidgets(Edit_Dict, ComboBox_Dict):
    """Emits all the signals for the lineEdits and ComboBoxes so they get
    updated"""
    for axis in ["X", "Y", "Z", "N"]:
        ComboBox_Dict[axis + "Axis"].currentIndexChanged.emit(1)


def setUpMovieFolder(Param_Dict):
    """Creates a folder for the movie pictures to be saved in."""
    directory = QW.QFileDialog.getExistingDirectory(None, "Select a directory "
                                                    "to save the pictures in",
                                                    Param_Dict["Directory"])
    if directory == "":
        GUILogger.warning("Evaluation stopped. Please select a valid directory.")
        return False
    date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    plotMode = Param_Dict["PlotMode"]  # for the fstring
    directory = f"{directory}/{plotMode}plots_{date}"
    mkdir(directory)
    GUILogger.log(29, f"The pictures are being saved to <b>{directory}</b>.")
    return directory


# %% Helper functions for plotting, including annotations and extrema calc:
def annotateStartEnd(Param_Dict, ax):
    """Annotates two boxes for start and end coordinates"""
    if not Param_Dict["LineAnno"]:
        return
    bboxArgs = {'boxstyle': 'square,pad=0.3', 'facecolor': 'white',
                'linewidth': 2, 'edgecolor': 'black', 'alpha': 0.5}
    startText, endText = createLineTexts(Param_Dict)
    ax.text(0.0, -0.14, startText, size=10, bbox=bboxArgs, ha="left", va="bottom",
            transform=ax.transAxes, **{"color": "black"})
    ax.text(1.0, -0.14, endText, size=10, bbox=bboxArgs, ha="right", va="bottom",
            transform=ax.transAxes, **{"color": "black"})


def calcExtrema(Param_Dict, ds, field, projCond):
    """Tries to calculate the extrema."""
    if projCond:
        # For a projection plot, we need to get the projected min and max
        # We also need to create new entries in the fieldMins
        minMaxArray = calcProjectionExtrema(Param_Dict, ds, field)
    else:
        try:
            minMaxArray = ds.all_data().quantities.extrema(field)
        except yt.utilities.exceptions.YTFieldNotFound:
            GUILogger.warning(f"Couldn't find {field} in the available fields")
            raise WorkingException
    return minMaxArray


def calcProjectionExtrema(Param_Dict, ds, field):
    """Creates dummy projection plots to then calculate the extrema in those.
    Returns a ytArray of these extrema"""
    try:
        if Param_Dict["ParticlePlot"]:
            projPlot = yt.ParticleProjectionPlot(ds, Param_Dict["NAxis"], field)
        else:
            projPlot = yt.ProjectionPlot(ds, Param_Dict["NAxis"], field)
    except yt.utilities.exceptions.YTFieldNotFound:
        GUILogger.warning(f"Couldn't find {field} in the available fields")
        return
    ZMin = projPlot.frb[field].min()
    ZMax = projPlot.frb[field].max()
    return yt.YTArray([ZMin, ZMax])


def checkExtremaForPlot(Param_Dict):
    """Performs a check on whether the extrema have been calculated for the
    necessary fields for a plot. If needed, calculate them.
    Parameters:
        Param_Dict: For checking whether the extrema have been calculated
    """
    mode = Param_Dict["PlotMode"]
    if mode == "Profile" or mode == "Phase":
        field = Param_Dict["XAxis"]
        # It doesn't matter which dictionary (fieldmin or fieldmax) we use.
        if field not in Param_Dict["FieldMins"].keys():
            Param_Dict["SignalHandler"].calculateExtrema("X")
    if mode == "Phase" or mode == "Profile" or mode == "Line":
        field = Param_Dict["YAxis"]
        if field not in Param_Dict["FieldMins"].keys():
            Param_Dict["SignalHandler"].calculateExtrema("Y")
    if mode != "Profile" and mode !="Line":
        field = Param_Dict["ZAxis"]
        if mode == "Projection":
            field = "Proj" + field
        if field not in Param_Dict["FieldMins"].keys():
            Param_Dict["SignalHandler"].calculateExtrema("Z")


def createTimestampText(Param_Dict):
    """Creates the text for a timestamp annotation"""
    ds = Param_Dict["CurrentDataSet"]
    timeUnit = ds.get_smallest_appropriate_unit(ds.current_time,
                                                quantity="time")
    time = ds.current_time.to_value(timeUnit)
    return f"t = {time:.1f} {timeUnit}"


def createLineTexts(Param_Dict):
    """Creates and returns the text for the line edit."""
    startNumbers = [Param_Dict[axis + "LStart"] for axis in ["X", "Y", "Z"]]
    endNumbers = [Param_Dict[axis + "LEnd"] for axis in ["X", "Y", "Z"]]
    startNumbers = yt.YTArray(startNumbers, Param_Dict["LineUnit"])
    endNumbers = yt.YTArray(endNumbers, Param_Dict["LineUnit"])
    ds = Param_Dict["CurrentDataSet"]
    lengthUnit = ds.get_smallest_appropriate_unit(max(startNumbers+endNumbers),
                                                  quantity="distance")
    startLengths = startNumbers.to_value(lengthUnit)
    endLengths = endNumbers.to_value(lengthUnit)
    startString = f"({startLengths[0]:.1f}), ({startLengths[1]:.1f}), ({startLengths[2]:.1f})"
    endString = f"({endLengths[0]:.1f}), ({endLengths[1]:.1f}), ({endLengths[2]:.1f})" 
    startString = f"Start: {startString} {lengthUnit}"
    endString = f"End: {endString} {lengthUnit}"
    return startString, endString


def drawTimestampBox(Param_Dict, ax):
    """Draw a custom timestamp annotation box like the one used by yt"""
    bboxArgs = {'boxstyle': 'square,pad=0.3', 'facecolor': 'black',
                'linewidth': 3, 'edgecolor': 'white', 'alpha': 0.5}
    text = createTimestampText(Param_Dict)
    ax.text(0.03, 0.96, text, size=15, bbox=bboxArgs, ha="left", va="top",
            transform=ax.transAxes, **{"color": "w"})


def getCalcQuanString(Param_Dict):
    """Compute the correct string for calculating the desired quantity.
    Requires all_data() to be defined as ad before plotting"""
    calcQuan = Param_Dict["TimeQuantity"]
    field = Param_Dict["YAxis"]
    unit = Param_Dict["YUnit"]
    if calcQuan == "weighted_average":
        calcQuan += "_quantity"
    if calcQuan in ["weighted_average_quantity", "weighted_variance"]:
        if Param_Dict["WeightField"] is None:
            weight = "ones"
        else:
            weight = Param_Dict["WeightField"]
        calcQuan = "quantities." + calcQuan + f"('{field}', '{weight}')"
    else:  # e.g. max('density')
        calcQuan = calcQuan + f"('{field}')"
    return f"ad.{calcQuan}.to_value('{unit}')"


def getCalcQuanName(Param_Dict):
    """Compute and return a definitive name for the calculated quantity with
    which the datasets can be associated with"""
    calcQuan = Param_Dict["TimeQuantity"]
    calcQuan = "_" + calcQuan
    if calcQuan in ["weighted_average", "weighted_variance"]:
        calcQuan += ("_" + str(Param_Dict["WeightField"]))
    return calcQuan


def issueAnnoWarning(plot, anno):
    """Unfortunately, grids are not annotated if the center is 0, 0 for a plot.
    Issue an error to the GUILogger if that is the case.
    Parameters:
        plot: yt slice/projection plot instance
        anno: String denoting the kind of annotation"""
    center = plot.center
    if not all(center):  # non-zero values are interpreted as True
        GUILogger.error(f"{anno} could not properly be drawn. This bug occurs if"
                        " one of the center coordinates is 0. Try setting them "
                        "to 1e-100 au or another very low value.")


# %% Functions needed for threading:
def calculateProfileAdditions(Param_Dict):
    """Calculates how many additional steps are needed for a profile plot"""
    length = len(Param_Dict["DataSeries"])
    if Param_Dict["XAxis"] == "time":
        # assuming the timesteps are equally distributed
        startTime = Param_Dict["FieldMins"]["time"]
        endTime = Param_Dict["FieldMaxs"]["time"]
        completeTimeDiff = endTime - startTime
        selectedTimeDiff = Param_Dict["XMax"] - Param_Dict["XMin"]
        return min(length, int(length*selectedTimeDiff/completeTimeDiff))+1
    elif Param_Dict["TimeSeriesProf"]:
        length = ceil(length/Param_Dict["ProfOfEvery"])
        return length
    else:
        return 0


def emitStatus(worker, message):
    """Emits a status message on the current worker or raises an exception
    which needs to be caught above."""
    if worker is None:
        return
    if worker._isRunning:
        GUILogger.debug(message)
        worker.progressUpdate.emit(message)
        worker.oldMessage = message
    else:
        raise WorkingException(f"You cancelled the plotting process \
                               while <b>{worker.oldMessage.lower()}.</b>")


def emitMultiStatus(worker, currentNumber, plotNumber):
    """Emits a multiProgressupdate on the current worker or raises an exception
    which needs to be caught above."""
    if worker is None:
        return
    if worker._isRunning:
        worker.multiProgress.emit()
    else:
        raise WorkingException(f"You cancelled the plotting process while \
                               <b>producing plot {currentNumber}/{plotNumber}</b>.")


class WorkingException(Exception):
    """Exception to raise while plotting"""
    pass


# %% Functions for setting up a file/series
def calculateKnownExtrema(Param_Dict, Edit_Dict):
    """Our Dataset already has some of the extrema as attributes, so we can add
    those to the Mins and Maxs.
    Parameters:
        Edit_Dict: To set the center edits"""
    ds = Param_Dict["CurrentDataSet"]
    axes = ["X", "Y", "Z"]
    if Param_Dict["Geometry"] == "cartesian":
        edgeList = ["x", "y", "z"]
    elif Param_Dict["Geometry"] == "cylindrical":
        edgeList = ["r", "z", "theta"]
    else:
        raise NotImplementedError("only cartesian and cylindrical geometries "
                                  "have been implemented so far")
    for i, field in enumerate(edgeList):
        minArray = ds.domain_left_edge
        maxArray = ds.domain_right_edge
        unit = Param_Dict["FieldUnits"][field]
        if field == "theta":
            minVal = minArray[i].value
            maxVal = maxArray[i].value
            minTextVal, maxTextVal = 0, 0
        else:
            minVal = yt.YTQuantity(ds.quan(minArray[i], 'code_length')).to_value(unit)
            maxVal = yt.YTQuantity(ds.quan(maxArray[i], 'code_length')).to_value(unit)
            minTextVal = yt.YTQuantity(minVal, unit).to_value(Param_Dict["GridUnit"])
            maxTextVal = yt.YTQuantity(maxVal, unit).to_value(Param_Dict["GridUnit"])
        Param_Dict["FieldMins"][field] = minVal
        Param_Dict["FieldMaxs"][field] = maxVal
        center = 0.5*(maxTextVal+minTextVal)
        cenEdit = Edit_Dict[axes[i] + "Center"]
        cenEdit.setText(f"{center:.3g}")
        cenEdit.textChanged.emit(cenEdit.text())


def resetExtrema(Param_Dict, Edit_Dict, Button_Dict, Label_Dict, ComboBox_Dict,
                 Window):
    """Resets FieldMin and FieldMax for all axes. Only needed when a new file
    is loaded."""
    QW.QApplication.setOverrideCursor(QC.Qt.WaitCursor)
    for axis in ["X", "Y", "Z"]:
        if Param_Dict["isValidFile"]:
            Button_Dict[axis + "Calc"].setToCalculate(Param_Dict, axis)
            Button_Dict[axis + "Calc"].show()
        if Param_Dict["isValidSeries"]:
            Button_Dict[axis + "Recalc"].setToRecalculate(axis, Window)
            Button_Dict[axis + "Recalc"].show()
        Edit_Dict[axis + "Min"].setPlaceholderText("default")
        Edit_Dict[axis + "Min"].turnTextBlue()
        Edit_Dict[axis + "Min"].setToolTip("Press 'Calculate Extrema' to get Extrema of this field")
        Edit_Dict[axis + "Max"].setPlaceholderText("default")
        Edit_Dict[axis + "Max"].turnTextBlue()
        Edit_Dict[axis + "Max"].setToolTip("Press 'Calculate Extrema' to get Extrema of this field")
    Param_Dict["FieldMins"] = {}
    Param_Dict["FieldMaxs"] = {}
    lU = Param_Dict["GridUnit"]
    keys = ["x", "y", "z", "dens", "temp", "r", "phi", "theta", "time"]
    values = [lU, lU, lU, "g/cm**3", "K", lU, "1", "1", "kyr"]
    for key, value in zip(keys, values):
        Param_Dict["FieldUnits"][key] = value
        Param_Dict["FieldUnits"]["Proj" + key] = value + "*cm"
    # convert the units into yt quantities
    for field, unit in Param_Dict["FieldUnits"].items():
        Param_Dict["FieldUnits"][field] = yt.units.YTQuantity(1, unit).units
    # Do the reset only for series or for single file mode:
    mode = Param_Dict["EvalMode"]
    for key in ["Mins", "Maxs", "Units"]:
        Param_Dict[mode + "Field" + key] = Param_Dict[ "Field" + key]
    for key in ["XCen", "YCen", "ZCen", "HorWidth", "VerWidth"]:
        Label_Dict[key + "Unit"].setText(Param_Dict["GridUnit"])
    for axis in ["X", "Y", "Z"]:
        Label_Dict[axis + "MinUnit"].setText(str(Param_Dict["FieldUnits"][Param_Dict[axis + "Axis"]]))
        Label_Dict[axis + "MaxUnit"].setText(str(Param_Dict["FieldUnits"][Param_Dict[axis + "Axis"]]))
    if Param_Dict["isValidFile"]:
        calculateKnownExtrema(Param_Dict, Edit_Dict)
    QW.QApplication.restoreOverrideCursor()


def updateComboBoxes(Param_Dict, ComboBox_Dict):
    """Updates the ComboBoxes with the content fitting the file and the current
    mode. If Particles are used, update with particle content."""
    # Now that the field lists are updated, also update the comboBoxes displays
    for i, axis in enumerate(["X", "Y", "Z"]):
        ComboBox_Dict[axis + "Axis"].disconnect()
        ComboBox_Dict[axis + "Axis"].clear()
        if Param_Dict["ParticlePlot"]:
            ComboBox_Dict[axis + "Axis"].addItems(Param_Dict["ParticleFields"])
            ComboBox_Dict[axis + "Axis"].setListWidth(500)
        else:
            ComboBox_Dict[axis + "Axis"].addItems(Param_Dict[axis + "Fields"])
            ComboBox_Dict[axis + "Axis"].setListWidth(200)
        if axis != "X":
            weightBox = ComboBox_Dict[axis + "Weight"]
            lastWeight = weightBox.currentText()
            weightBox.disconnect()
            weightBox.clear()
            if Param_Dict["ParticlePlot"]:
                weightBox.addItem(Param_Dict["WeightFields"][0])
                weightBox.addItems(Param_Dict["ParticleFields"])
                weightBox.setListWidth(500)
            else:
                weightBox.addItems(Param_Dict["WeightFields"])
                weightBox.setListWidth(200)
            weightBox.setCurrentText(lastWeight)  # if not possible, just return to None
    # Set default values for y axis to second entry
    ComboBox_Dict["YAxis"].setCurrentText("temp")
    ComboBox_Dict["XAxis"].currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getAxisInput("X"))
    ComboBox_Dict["YAxis"].currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getAxisInput("Y"))
    ComboBox_Dict["ZAxis"].currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getAxisInput("Z"))
    ComboBox_Dict["NAxis"].currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getAxisInput("N"))
    ComboBox_Dict["YWeight"].currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getWeightField("Y"))
    ComboBox_Dict["ZWeight"].currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getWeightField("Z"))
    Param_Dict["SignalHandler"].getWeightField("Y")
    Param_Dict["SignalHandler"].getWeightField("Z")


def updateFields(Param_Dict, ComboBox_Dict):
    """Updates ComboBoxes with the current fields used
    Parameters:
        Param_Dict: For the current field lists
        Box_Dict: Dictionary for ComboBoxes
    """
    QW.QApplication.setOverrideCursor(QC.Qt.WaitCursor)
    ds = Param_Dict["CurrentDataSet"]
    Param_Dict["WeightFields"] = ["None", "cell_mass", "dens", "temp"]
    try:
        point = ds.point([0, 0, 0])  # sampling point
        for i in sorted(ds.derived_field_list):
            # in derived field lists, all of the entries are sorted in separate
            # lists: [['gas', 'dens'], ['gas', 'dens']] etc.
            if i[0] == 'gas':
                for axis in ["X", "Y", "Z", "Weight"]:
                    Param_Dict[axis + "Fields"].append(i[1])
            if i[0] == 'io':
                shape = point[i].shape
                if not (len(shape) > 1 and shape[1] > 1):
                    Param_Dict["ParticleFields"].append(i[1])
    except Exception as e:
        GUILogger.critical("An error occured while trying to load in "
                           f"the fields: <b>{e}</b>.")
        GUILogger.critical("The reason may be a derived field with "
                           "unknown dependencies. You may need to "
                           "restart the application. If you're running"
                           " python from an iPython console, you even "
                           " need to restart this. Sorry.")
        raise Exception
    try:
        Param_Dict["ParticleFields"].remove("mesh_id")
    except ValueError:
        pass
    updateNormalAxis(Param_Dict, ComboBox_Dict)
    updateComboBoxes(Param_Dict, ComboBox_Dict)
    QW.QApplication.restoreOverrideCursor()


def updateGeometry(Param_Dict, CheckBox_Dict, RadioDict_Dict, Edit_Dict,
                   Label_Dict):
    """Checks the geometry of the DataSet and stores it. Updates the field list
    base according to geometry and hides some widgets that would cause errors
    if used on unfitting geometries.
    Also Check the DataSet for relevant fields and reset the knowledge of the
    Extrema
    Parameters:
        Param_Dict: For storing geometry
        CheckBox_Dict: For hiding error-causing checkboxes
    """
    ds = Param_Dict["CurrentDataSet"]
    geometry = ds.geometry
    Param_Dict["Geometry"] = geometry
    Param_Dict["YFields"] = ["dens", "temp"]
    Param_Dict["ZFields"] = ["dens", "temp"]
    checkBoxKeys = ["Scale", "Grid", "VelVectors",
                    "VelStreamlines", "MagVectors", "MagStreamlines",
                    "Contour", "ParticleAnno"]
    if geometry == 'cartesian':
        RadioDict_Dict["1DOptions"]["Line"].setEnabled(True)
        Param_Dict["XFields"] = ['x', 'y', 'z']
        Param_Dict["NFields"] = ['x', 'y', 'z']
    elif geometry == 'cylindrical':
        RadioDict_Dict["1DOptions"]["Line"].setEnabled(False)
        if Param_Dict["PlotMode"] == "Line":
            Param_Dict["PlotMode"] = "Profile"  # is set at a later p.o.t.
        Param_Dict["XFields"] = ['r', 'z', 'theta']
        Param_Dict["NFields"] = ['z', 'r', 'theta']
        for key in checkBoxKeys:
            CheckBox_Dict[key].hide()
        Edit_Dict["PSlabWidth"].hide()
    elif geometry == 'spherical':
        RadioDict_Dict["1DOptions"]["Line"].setEnabled(False)
        if Param_Dict["PlotMode"] == "Line":
            Param_Dict["PlotMode"] = "Profile"
        Param_Dict["XFields"] = ['r', 'theta', 'phi']
        Param_Dict["NFields"] = ['r', 'theta', 'phi']
        for key in checkBoxKeys:
            CheckBox_Dict[key].hide()
        Edit_Dict["PSlabWidth"].hide()
    else:
        alertUser("Unknown geometry of the file. Please supply a file that "
                  "uses cartesian, cylindrical or spherical geometry")
    for axis, field in zip(["X", "Y", "Z"], Param_Dict["XFields"]):
        Label_Dict[axis + "Center"].setText(f"Center {field}:")


def updateNormalAxis(Param_Dict, ComboBox_Dict):
    """Updates the Combobox for the three fields for the normal axis"""
    normBox = ComboBox_Dict["NAxis"]
    normBox.disconnect()
    normBox.clear()
    normBox.addItems(Param_Dict["NFields"])
    normBox.setCurrentText(Param_Dict["NAxis"])
    normBox.currentIndexChanged.connect(lambda: Param_Dict["SignalHandler"].getAxisInput("N"))
    Param_Dict["SignalHandler"].getAxisInput("N")


# %% Functions for line drawing:
def getCoordInput(Param_Dict, event, key):
    """When the user clicks on the canvas, read out the coordinates and store
    them in the Parameter Dictionary.
    Parameters:
        Param_Dict: Parameter Dictionary
        event: matplotlib event with necessary data
        key: "start" or "end" depending on press or release type
    """
    # We only want data out of the main axis
    heightAxis = Param_Dict["CurrentPlotWindow"].Param_Dict["NAxis"].upper()
    height = Param_Dict["CurrentPlotWindow"].Param_Dict[heightAxis + "Center"]
    if str(event.inaxes)[:11] == "AxesSubplot":
        if key == "start":
            Param_Dict["XLStart"] = event.xdata
            Param_Dict["YLStart"] = event.ydata
            Param_Dict["ZLStart"] = height
        if key == "end":
            Param_Dict["XLEnd"] = event.xdata
            Param_Dict["YLEnd"] = event.ydata
            Param_Dict["ZLEnd"] = height


def shuffleCoords(Param_Dict):
    """The coordinates may need to be shuffled if the user doesn't have the
    z-axis as normal vector.
    """
    starts = ["XLStart", "YLStart", "ZLStart"]
    ends = ["XLEnd", "YLEnd", "ZLEnd"]
    # save the values for shuffling
    svalues = [Param_Dict[key] for key in starts]
    evalues = [Param_Dict[key] for key in ends]
    if Param_Dict["NAxis"] == "x":
        # This shuffles the list in a cyclic way: [1, 2, 3] -> [2, 3, 1]
        svalues.append(svalues.pop(0))
        evalues.append(evalues.pop(0))
        # and once more
        svalues.append(svalues.pop(0))
        evalues.append(evalues.pop(0))
    elif Param_Dict["NAxis"] == "y":
        svalues.append(svalues.pop(0))
        evalues.append(evalues.pop(0))
    elif Param_Dict["NAxis"] == "z":
        # no shuffling needed
        pass
    else:
        GUILogger.error("Something went wrong when transferring the coordinates to LinePlot")
    for i in range(3):
        Param_Dict[starts[i]] = svalues[i]
        Param_Dict[ends[i]] = evalues[i]


def changeToLinePlot(Param_Dict, Edit_Dict):
    """After a line is drawn, change all of the linePlot Settings"""
    keys = ["XLStart", "YLStart", "ZLStart", "XLEnd", "YLEnd", "ZLEnd"]
    for i in range(6):
        Edit_Dict[keys[i]].setText(f"{Param_Dict[keys[i]]:.3g}")


def printParam_Dict(Param_Dict):
    for key, value in Param_Dict.items():
        print(f"{key}: {value}")
