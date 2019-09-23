# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

This file serves as a database where one can look up all of the dictionary
keys and their purpose.
These keys are connected to input/actual widgets at a later point in the code.

Each time a new key is added, it should be added here as well.
[sorted in alphabetical order]
"""


def createButton_Dict():
    """Creates a dictionary with all of the keys for the Button widgets.
    The widgets are assigned later using the function "createAllButtons"."""
    buttons = ["Open",  # For opening a file/series
               "Evaluate",  # For plotting a single file
               "PlotAll",  # For opening a dialog to plot multiple files
               "WriteScript",  # For opening a dialog to write the settings to script
               "PlotHelp1D", "PlotHelp2D",  # Buttons for help on plots
               "MakeLinePlot",  # For drawing a line to make line plot
               "AddDerField",  # For opening a dialog to add a derived field
               "XCalc", "YCalc", "ZCalc",  # For calculating extrema
               "XRecalc", "YRecalc", "ZRecalc",  # For opening a dialog to recalculate extrema
               "QuickCart", "QuickCyli", "QuickSeries"] # some test mode buttons
    Button_Dict = dict(zip(buttons, [""]*len(buttons)))
    return Button_Dict


def createCheckBox_Dict():
    """Creates a dictionary with all of the keys for the CheckBox widgets.
    The widgets are assigned later using the function "createAllCheckBoxes"."""
    boxes = ["Timestamp", "Scale", "Grid", "VelVectors", "VelStreamlines",
             "MagVectors", "MagStreamlines", "Contour", "ParticleAnno",
             "LineAnno",  # For toggling Annotations
             "XLog", "YLog", "ZLog",  # For toggling log scaling
             "DomainDiv",  # For toggling division by domain length for projection plots
             "SetAspect",  # For toggling IgnoreAspect for slice and projection plots
             "AddProfile",  # For adding a second profile to a profile plot
             "TimeSeriesProf",  # For toggling multiple profiles for a profile plot in time series mode
             "ParticlePlot"]  # For toggling particle plots
    CheckBox_Dict = dict(zip(boxes, [""]*len(boxes)))
    return CheckBox_Dict


def createComboBox_Dict():
    """Creates a dictionary with all of the keys for the CheckBox widgets.
    The widgets are assigned later using the function "createAllCheckBoxes"."""
    boxes = ["XAxis", "YAxis", "ZAxis",  # For the field names for the axes
             "NAxis",  # For the axis-aligned normal axis
             "YWeight", "ZWeight",  # For the weight fields
             "TimeQuantity"]  # For the quantity to be calculated for profile plots with respect to time
    ComboBox_Dict = dict(zip(boxes, [""]*len(boxes)))
    return ComboBox_Dict


def createEdit_Dict():
    """Creates a dictionary with all of the keys for the LineEdit widgets.
    The widgets are assigned later using the function "createAllEdits"."""
    edits = ["XMin", "YMin", "ZMin",  # For the minima of the fields
             "XMax", "YMax", "ZMax",  # For the maxima
             "XUnit", "YUnit", "ZUnit",  # For the units of the fields
             "LineUnit", "GridUnit",  # For the units used for (line, slice and proj)
             "Zoom",  # For the zoom (slice and proj)
             "XCenter", "YCenter", "ZCenter",  # For center coords (slice and proj)
             "HorWidth", "VerWidth",  # For the grid width (slice and proj)
             "XLStart", "YLStart", "ZLStart",  # For start point for line plots
             "XLEnd", "YLEnd", "ZLEnd",  # For end point for line plots
             "XNormDir", "YNormDir", "ZNormDir",  # For Off-Axis normal vector input (slice and proj)
             "XNormNorth", "YNormNorth", "ZNormNorth",  # For north vector input (slice and proj)
             "PlotTitle",  # For the plot title
             "ColorScheme"]  # For the color scheme
    Edit_Dict = dict(zip(edits, [""]*len(edits)))
    return Edit_Dict


def createLabel_Dict():
    """Creates a dictionary with all of the keys for the Label widgets.
    The widgets are assigned later using the function "createAllLabels"."""
    labels = ["XMinUnit", "YMinUnit", "ZMinUnit",  # For the minimum units
              "XMaxUnit", "YMaxUnit", "ZMaxUnit",  # For the maximum units
              "XCenUnit", "YCenUnit", "ZCenUnit",  # For the center coord units (slice and proj)
              "HorWidthUnit", "VerWidthUnit",  # For the grid width units (slice and proj)
              "CurrentDataSet", "DataSetTime",  # For information about the current dataset
              "Geometry", "Dimensions",  # For information about the current dataset
              "LineLength"]  # For the line length of a line plot line
    Label_Dict = dict(zip(labels, [""]*len(labels)))
    return Label_Dict


def createMisc_Dict():
    """Creates a dictionary with all of the keys for miscellaneous widgets that
    didn't fit any other category.
    The widgets are assigned later using functions for each of them."""
    miscs = ["SeriesSlider",  # Slider for choosing a file in time series mode
             "ProfileSpinner", # Spinner for choosing how many files are skipped for multiple profiles
             "LogBox"]  # TextBox for displaying logger information
    Misc_Dict = dict(zip(miscs, [""]*len(miscs)))
    return Misc_Dict


def createParam_Dict():
    """Creates a dictionary with all of the keys needed for storing the data of
    the GUI.
    It is important we have "X", "Y" and "Z" in front because this makes
    accessing everything easier. Example:
    for axis in ["X", "Y", "Z"]:
        print(f"The field for the {axis}-axis is {Param_Dict[axis+"Axis"]}.)
    """
    # keys linked to the field comboBox and normal axis:
    field = ["XAxis", "YAxis", "ZAxis", "NAxis"]
    fieldDef = ["x", "y", "dens", "z"]
    # keys for storing the available fields. Updated once a file is loaded:
    possField = ["XFields", "YFields", "ZFields", "NFields", "ParticleFields",
                 "WeightFields"]
    possFieldDef = [["x", "y", "z"], ["dens", "temp"], ["dens", "temp"],
                    ["x", "y", "z"], [], ["None", "cell_mass", "dens", "temp"]]
    # keys linked to the extrema and unit inputs.
    # Updated first upon start of GUI and partially set through config:
    extrema = ["XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax",
               "XUnit", "YUnit", "ZUnit", "LineUnit", "oldGridUnit", "GridUnit"]
    extremaDef = ["", "", "", "", "", "",
                  "cm", "K", "g/cm**3", "au", "au", "au"]
    # keys for storing available extrema and default units.
    # Updated once a file is loaded:
    extrStore = ["FieldMins", "FieldMaxs", "FieldUnits"]
    extrStoreDef = [{}, {}, {}]
    # keys linked to CheckBoxes for the log settings of the axes.
    # Log cannot be set if min < 0.
    log, logDef = ["XLog", "YLog", "ZLog"], [False, True, True]
    # For slice and proj, center coordinates, zoom and width have to be saved.
    # Linked to the LineEdits. Updated once a file is loaded:
    domain = ["XCenter", "YCenter", "ZCenter", "Zoom", "HorWidth", "VerWidth",
              "HorDomainWidth", "VerDomainWidth"]  # last two are for the max.
    domainDef = [0.0, 0.0, 0.0, 1.0, "", "", 1, 1]
    # Also, specifications for the off-axis normal + north vector need to be saved:
    norm = ["XNormDir", "YNormDir", "ZNormDir",
            "XNormNorth", "YNormNorth", "ZNormNorth"]
    normDef = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0]
    # The following are specific quantities needed for certain tasks. Note that
    # even though there are two ComboBoxes for the WeightField, only one entry
    # is set here and linked to both.
    quan = ["ColorScheme", "WeightField", "SetAspect", "DomainDiv"]
    quanDef = ["viridis", "None", False, False]
    # For line plots, the start and end points linked to the LineEdits have
    # to be saved. Updated once "Draw line for line plot" is drawn.
    point = ["XLStart", "YLStart", "ZLStart", "XLEnd", "YLEnd", "ZLEnd"]
    pointDef = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    # For profile plots, there are some additional options which are stored
    # under the following keys:
    prof = ["TimeQuantity", "AddProfile", "TimeSeriesProf", "ProfOfEvery"]
    profDef = ["max", False, False, 1]
    # keys for the annotations, usually linked to CheckBoxes:
    anno = ["PlotTitle", "Timestamp", "Scale", "Grid", "VelVectors",
            "VelStreamlines", "MagVectors", "MagStreamlines", "Contour",
            "ParticleAnno", "PSlabWidth", "LineAnno"]
    annoDef = ["", True, False, False, False, False, False, False, False,
               False, 1, False]
    # keys for the modes selectable through the radio buttons:
    modes = ["EvalMode", "PlotMode", "DimMode", "NormVecMode"]
    modesDef = ["Single", "Slice", "2D", "Axis-Aligned"]
    # keys for file/series information. Updated once a file is loaded:
    file = ["isValidFile", "isValidSeries", "Filename", "Directory",
            "Seriesname", "Geometry"]
    fileDef = [False, False, "No file selected", "(Config)", "", ""]
    # keys for storing single dataset information:
    single = ["SingleDataSet", "DataSetTime", "DataSetPlotWindow"]
    singleDef = ["(ytDataset)", "(ytQuantity)", "(PlotWindow)"]
    # keys for storing series information (most of it in DataSetDict:
    series = ["DataSeries", "DataSetDict"]
    seriesDef = ["", {}]
    # keys for keeping track of the current file and dataset:
    curr, currDef = ["CurrentDataSet", "CurrentPlotWindow"], ["", ""]
    # keys not fitting into any category: Toggling particle plots, the type of
    # a valid plot, the Signal Handler, the dictionary for keeping track of
    # the derived fields, and a mode for testing:
    misc = ["ParticlePlot", "isValidPlot", "SignalHandler", "NewDerFieldDict",
            "OnlyEvery", "TestingMode"]
    miscDef = [False, "(PlotType)", "(QObject)", {}, 1, False]
    keys = (field + possField + extrema + extrStore + log + domain + norm +
            quan + point + prof + anno + modes + file + single + series +
            curr + misc)
    values = (fieldDef + possFieldDef + extremaDef + extrStoreDef + logDef +
              domainDef + normDef + quanDef + pointDef + profDef + annoDef +
              modesDef + fileDef + singleDef + seriesDef + currDef + miscDef)
    Param_Dict = dict(zip(keys, values))
    return Param_Dict


def createRadioDict_Dict():
    """Creates a dictionary containing the keys for the dictionaries containing
    the separate RadioButton groups.
    The widgets are assigned later using the function "createAllRadioDicts"."""
    dicts = ["EvalMode",  # A radio group for evaluation mode (single file/time series)
             "NormVecMode", # For the normal vector (axis-aligned/off-axis)
             "DimMode",  # For dimensions (1D/2D)
             "1DOptions",  # For 1D-plots (profile/line)
             "2DOptions"]  # For 2D-plots (phase/slice/projection)
    RadioDict_Dict = dict(zip(dicts, [""]*len(dicts)))
    return RadioDict_Dict


def createStatus_Dict():
    """Creates a dictionary containing the keys for the status bar and the
    labels displayed on it.
    The widgets are assigned later using the function "createAllStatusInfo"."""
    wids = ["Bar",  # The status bar itself, host of the labels
            "Status",  # For current status information
            "Dir", "File", "Series"]  # For permanent file/series information
    Status_Dict = dict(zip(wids, [""]*len(wids)))
    return Status_Dict


def createWid_Dict():
    """Creates a dictionary containing the keys for some small widgets that
    host other widgets in BoxLayouts.
    The widgets are assigned later using the function "createAllWidgets"."""
    wids = ["EvalMode", "2DOptions", "1DOptions", "DimMode", "NormVecMode",  # Layouts containing radio buttons
            "PlotOptions",  # Layout containing "Lower part" of the GUI
            "FileOptions",  # Layout containing "Upper right part" of the GUI
            "XAxis", "YAxis", "ZAxis",  # Layout for the axes
            "NAxis", "SlcProjOptions",  # Layouts for extra slice and projection plot options
            "NormInput", "NorthInput",  # Layouts for the LineEdits for off-axis normal options
            "AnnotationOptions",  #Layout for annotations
            "LineOptions",  # Layout for extra line plot options
            "ProfileOptions",  # Layout for extra profile plot options
            "DataSeriesLabels",  # Layout for file information labels
            "TopLayout",  # Layout for the file options and the plot window
            "ParticlePlot"]  # Layout for the particle plot CheckBox
    Wid_Dict = dict(zip(wids, [""]*len(wids)))
    return Wid_Dict
