# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Contains functions and methods concerning the plots done while the GUI is
running.

The module is structured as follows:
    - Function to draw the plot
    - Functions for slice and projection plots
    - Functions for line and phase plots
    - Functions for profile plots: Normal, multiple and timed
    - Functions for setting the axis settings (general, and profile)
"""
from copy import copy
import numpy as np
from math import ceil
import yt
from simgui_modules.logging import GUILogger
from simgui_modules.utils import getCalcQuanName, getCalcQuanString, \
        emitStatus, issueAnnoWarning


# %% Function to draw the plot on the canvas of the PlotWindow
def finallyDrawPlot(plot, Param_Dict, worker):
    """Do the final steps for plotting
    Parameters:
        plot: yt Plot object
        Param_Dict: For passing parameters
        worker: For giving status updates to the progress bar
    """
    plotCopy1 = copy(plot)
    plotWindow = Param_Dict["CurrentPlotWindow"]
    plotWindow.startPlot(plotCopy1, Param_Dict, worker=worker)


# %% Functions for slice and projection plots
def annotatePlot(Param_Dict, plot):
    """Annotates the plot according to the selection of the user.
    Tutorial:
        https://yt-project.org/doc/visualizing/callbacks.html"""
    plot.annotate_title(Param_Dict["PlotTitle"])
    if Param_Dict["Timestamp"]:
        plot.annotate_timestamp(corner='upper_left', draw_inset_box=True)
    if Param_Dict["Geometry"] == "cartesian":
        if Param_Dict["Scale"]:
            plot.annotate_scale(corner='upper_right')
        if Param_Dict["Contour"]:
            plot.annotate_contour(Param_Dict["ZAxis"])
        if Param_Dict["VelVectors"]:
            plot.annotate_velocity(normalize=True)
        if Param_Dict["NormVecMode"] == "Axis-Aligned":
            if Param_Dict["Grid"]:
                plot.annotate_grids()
                issueAnnoWarning(plot, "Grids")
            if Param_Dict["VelStreamlines"]:
                issueAnnoWarning(plot, "Velocity streamlines")
                if Param_Dict["NAxis"] == "x":
                    plot.annotate_streamlines("velocity_y", "velocity_z")
                elif Param_Dict["NAxis"] == "y":
                    plot.annotate_streamlines("velocity_x", "velocity_z")
                elif Param_Dict["NAxis"] == "z":
                    plot.annotate_streamlines("velocity_x", "velocity_y")
            if Param_Dict["MagVectors"]:
                plot.annotate_magnetic_field(normalize=True)
            if Param_Dict["MagStreamlines"]:
                issueAnnoWarning(plot, "Magnetic field streamlines")
                if Param_Dict["NAxis"] == "x":
                    plot.annotate_streamlines("magy", "magz")
                elif Param_Dict["NAxis"] == "y":
                    plot.annotate_streamlines("magx", "magz")
                elif Param_Dict["NAxis"] == "z":
                    plot.annotate_streamlines("magx", "magy")
        if Param_Dict["ParticleAnno"] and not Param_Dict["ParticlePlot"]:
            if Param_Dict["PSlabWidth"] == "" or float(Param_Dict["PSlabWidth"]) == 0:
                Param_Dict["PSlabWidth"] = 1
            height = abs(Param_Dict["FieldMins"]["DomainHeight"] - Param_Dict["FieldMaxs"]["DomainHeight"])
            if Param_Dict["Zoom"] == 1:
                GUILogger.warning("When annotating particles, you may need a "
                                  "zoom above 1 for proper annotations")
            plot.annotate_particles(float(Param_Dict["PSlabWidth"])*height, p_size=3.0)
    elif Param_Dict["Geometry"] == "cylindrical":
        if Param_Dict["Grid"]:
            plot.annotate_grids()


def SlicePlot(Param_Dict, worker):
    """Takes a DataSet object loaded with yt and performs a slicePlot on it.
    Parameters:
        Param_Dict: Dict with Parameters
    """
    ds = Param_Dict["CurrentDataSet"]
    gridUnit = Param_Dict["GridUnit"]
    c0 = yt.YTQuantity(Param_Dict["XCenter"], gridUnit)
    c1 = yt.YTQuantity(Param_Dict["YCenter"], gridUnit)
    if Param_Dict["Geometry"] == "cartesian":
        c2 = yt.YTQuantity(Param_Dict["ZCenter"], gridUnit)
    else:
        c2 = Param_Dict["ZCenter"]
    field = Param_Dict["ZAxis"]
    width = (Param_Dict["HorWidth"], gridUnit)
    height = (Param_Dict["VerWidth"], gridUnit)
    if Param_Dict["NormVecMode"] == "Axis-Aligned":
        plot = yt.AxisAlignedSlicePlot(ds, Param_Dict["NAxis"], field,
                                       axes_unit=Param_Dict["GridUnit"],
                                       fontsize=14, center=[c0, c1, c2],
                                       width=(width, height))
    else:
        normVec = [Param_Dict[axis + "NormDir"] for axis in ["X", "Y", "Z"]]
        northVec = [Param_Dict[axis + "NormNorth"] for axis in ["X", "Y", "Z"]]
        plot = yt.OffAxisSlicePlot(ds, normVec, field, north_vector=northVec,
                                   axes_unit=Param_Dict["GridUnit"],
                                   fontsize=14, center=[c0, c1, c2],
                                   width=(width, height))
    emitStatus(worker, "Setting slice plot modifications")
    # Set min, max, unit log and color scheme:
    setAxisSettings(plot, Param_Dict, "Z")
#    # yt will automatically make it quadratic, so we'll set the individual
#    plot.set_width((max(width, height), gridUnit))  # width and height later
    plot.zoom(Param_Dict["Zoom"])
    emitStatus(worker, "Annotating the slice plot")
    annotatePlot(Param_Dict, plot)
    finallyDrawPlot(plot, Param_Dict, worker)


def ProjectionPlot(Param_Dict, worker):
    """Takes a DataSet object loaded with yt and performs a projectionPlot on
    it.
    Parameters:
        Param_Dict: Dict with Parameters
    """
    ds = Param_Dict["CurrentDataSet"]
    field = Param_Dict["ZAxis"]
    if Param_Dict["DomainDiv"]:
        # in case the user wants to divide everything by the domain_height,
        # we define a new field which is just the old field divided by height
        # and then do a projectionPlot for that.
        height = Param_Dict["FieldMaxs"]["DomainHeight"] - Param_Dict["FieldMins"]["DomainHeight"]
        field = "Normed " + field
        unit = yt.units.unit_object.Unit(Param_Dict["ZUnit"] + "/cm")
        realHeight = height.to_value("au")  # Important! Bugs occur if we just used "height"
        def _NormField(field, data):
            return data[Param_Dict["ZAxis"]]/realHeight/yt.units.au
        if Param_Dict["ParticlePlot"]:
            ds.add_field(("io", field), function=_NormField,
                     units="auto", dimensions=unit.dimensions,
                     force_override=True, particle_type=True)
        else:
            ds.add_field(("gas", field), function=_NormField,
                         units="auto", dimensions=unit.dimensions,
                         force_override=True)
    gridUnit = Param_Dict["GridUnit"]
    c0 = yt.YTQuantity(Param_Dict["XCenter"], gridUnit)
    c1 = yt.YTQuantity(Param_Dict["YCenter"], gridUnit)
    if Param_Dict["Geometry"] == "cartesian":
        c2 = yt.YTQuantity(Param_Dict["ZCenter"], gridUnit)
    else:
        c2 = Param_Dict["ZCenter"]
    width = (Param_Dict["HorWidth"], gridUnit)
    height = (Param_Dict["VerWidth"], gridUnit)
    if Param_Dict["ParticlePlot"]:
        plot = yt.ParticleProjectionPlot(ds, Param_Dict["NAxis"], field,
                                         axes_unit=Param_Dict["GridUnit"],
                                         weight_field=Param_Dict["WeightField"],
                                         fontsize=14, center=[c0, c1, c2],
                                         width=(width, height))
    else:
        if Param_Dict["NormVecMode"] == "Axis-Aligned":
            plot = yt.ProjectionPlot(ds, Param_Dict["NAxis"], field,
                                     axes_unit=Param_Dict["GridUnit"],
                                     weight_field=Param_Dict["WeightField"],
                                     fontsize=14, center=[c0, c1, c2],
                                     width=(width, height))
        else:
            normVec = [Param_Dict[axis + "NormDir"] for axis in ["X", "Y", "Z"]]
            northVec = [Param_Dict[axis + "NormNorth"] for axis in ["X", "Y", "Z"]]
            plot = yt.OffAxisProjectionPlot(ds, normVec, field,
                                            north_vector=northVec,
                                            weight_field=Param_Dict["WeightField"],
                                            axes_unit=Param_Dict["GridUnit"],
                                            fontsize=14, center=[c0, c1, c2],
                                            width=(width, height))
    emitStatus(worker, "Setting projection plot modifications")
    # Set min, max, unit log and color scheme:
    setAxisSettings(plot, Param_Dict, "Z")
    plot.zoom(Param_Dict["Zoom"])
    emitStatus(worker, "Annotating the projection plot")
    annotatePlot(Param_Dict, plot)
    finallyDrawPlot(plot, Param_Dict, worker)


# %% Functions for line and phase plots:
def LinePlot(Param_Dict, worker):
    """Takes a DataSet object loaded with yt and performs a linePlot with
    currently entered start- and endpoints on it.
    Parameters:
        ds: yt DataSet
        Param_Dict: Dict with Parameters
    """
    ds = Param_Dict["CurrentDataSet"]
    startends = ["XLStart", "YLStart", "ZLStart", "XLEnd", "YLEnd", "ZLEnd"]
    valueList = []
    for key in startends:
        value = yt.units.YTQuantity(Param_Dict[key],
                                    Param_Dict["oldGridUnit"]).to_value(ds.quan(1, 'code_length').units)
        valueList.append(value)
    npoints = 512
    plot = yt.LinePlot(ds, Param_Dict["YAxis"], valueList[:3], valueList[3:],
                       npoints, fontsize=14)
    emitStatus(worker, "Setting line plot modifications")
    plot.annotate_legend(Param_Dict["YAxis"])
    setAxisSettings(plot, Param_Dict, "Y")
    plot.set_x_unit(Param_Dict["LineUnit"])
    emitStatus(worker, "Annotating the line plot")
    plot.annotate_title(Param_Dict["YAxis"], Param_Dict["PlotTitle"])
    finallyDrawPlot(plot, Param_Dict, worker)


def PhasePlot(Param_Dict, worker):
    """Takes a DataSet object loaded with yt and performs a phasePlot on it.
    Parameters:
        Param_Dict: to access the relevant parameters
    """
    if Param_Dict["WeightField"] is None:
        GUILogger.warning('Having <font color="DarkViolet">None</font> as the '
                          "weight field just accumulates, "
                          "so the extrema might be inaccurate.")
    ds = Param_Dict["CurrentDataSet"]
    XField, YField, ZField = Param_Dict["XAxis"], Param_Dict["YAxis"], \
        Param_Dict["ZAxis"]
    ad = ds.all_data()
    if Param_Dict["ParticlePlot"]:
        plot = yt.ParticlePhasePlot(ad, XField, YField, ZField,
                                    weight_field=Param_Dict["WeightField"],
                                    fontsize=14)
    else:
        plot = yt.PhasePlot(ad, XField, YField, ZField,
                            weight_field=Param_Dict["WeightField"],
                            fontsize=14)
    emitStatus(worker, "Setting phase plot modifications")
    # Set min, max, unit log and color scheme:
    setAxisSettings(plot, Param_Dict, "X")
    setAxisSettings(plot, Param_Dict, "Y")
    setAxisSettings(plot, Param_Dict, "Z")
    emitStatus(worker, "Annotating the phase plot")
    plot.annotate_title(Param_Dict["PlotTitle"])
    finallyDrawPlot(plot, Param_Dict, worker)


# %% Functions for profile plots: Normal, multiple and timed:
def ProfilePlot(Param_Dict, worker):
    """Takes a DataSet object loaded with yt and performs a ProfilePlot with
    fields on it.
    Parameters:
        Param_Dict: Dict with Parameters
    """
    if Param_Dict["XAxis"] == "time":
        arr, labels = createProfWithTimeForX(Param_Dict, worker)
    elif Param_Dict["TimeSeriesProf"]:
        arr, labels = createMultipleProfiles(Param_Dict, worker)
    else:
        arr, labels = createNormalProfile(Param_Dict)
    if Param_Dict["WeightField"] is None and Param_Dict["XAxis"] != "time":
        GUILogger.warning('Having <b><font color="DarkViolet">None</font></b> '
                          "as the weight field just accumulates, "
                          "so the extrema might be inaccurate.")
    Canvas = Param_Dict["CurrentPlotWindow"]
    Canvas.makeProfilePlot(Param_Dict, arr, labels, worker)


def createNormalProfile(Param_Dict):
    """Create a Profile plot for the selected x-and y-field. Return an array
    containing the data and a label.
    Parameters:
        Param_Dict: For the fields and DataSets to be plotted.
    Returns:
        arr: list containing two YTArrays having the x-field as the first and
             the y-field as second entry.
    """
    # Create a data container to hold the whole dataset.
    ds = Param_Dict["CurrentDataSet"]
    ad = ds.all_data()
    # Create a 1d profile of density vs. temperature.
    prof = yt.create_profile(ad, Param_Dict["XAxis"],
                             fields=[Param_Dict["YAxis"]],
                             weight_field=Param_Dict["WeightField"])
    labels = [Param_Dict["YAxis"]]
    arr = [prof.x, prof[Param_Dict["YAxis"]]]
    return arr, labels


def createMultipleProfiles(Param_Dict, worker):
    """Make a profile plot for each of the requested times and return them so
    they can be plotted.
    Parameters:
        Param_Dict: For the fields and DataSets to be plotted.
    Returns:
        arr: list containing YTArrays having the x-field as the first and the
             y-fields as second and following entries
        labels: the labels for the rows.
    """
    GUILogger.info("This may take some time.")
    onlyEvery = Param_Dict["ProfOfEvery"]
    if onlyEvery == 1:
        numString = ""
    else:
        suf = lambda n: "%d%s "%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
        numString = suf(onlyEvery)
    GUILogger.log(29, "Creating a profile for every {}dataset of the series...".format(numString))
    # the user can input to only plot every nth file:
    yt.enable_parallelism(suppress_logging=True)
    storage = {}
    labels = []
    i = 0
    ts = Param_Dict["DataSeries"]
    length = ceil(len(ts)/onlyEvery)
    if Param_Dict["YAxis"] in Param_Dict["NewDerFieldDict"].keys():
        for ds in ts:
            if i % onlyEvery == 0:
                # Create a data container to hold the whole dataset.
                ad = ds.all_data()
                # Create a 1d profile of xfield vs. yfield:
                prof = yt.create_profile(ad, Param_Dict["XAxis"],
                                         fields=[Param_Dict["YAxis"]],
                                         weight_field=Param_Dict["WeightField"])
                # Add labels
                time = Param_Dict["DataSetDict"][str(ds) + "Time"]
                label = "{} at {:.3g} ".format(Param_Dict["YAxis"], time.value)
                label += str(time.units)
                labels.append(label)
                storage[str(i)] = prof[Param_Dict["YAxis"]]
                progString = f"{int(i/onlyEvery+1)}/{length} profiles done"
                emitStatus(worker, progString)
                if i % ceil(length/10) == 0:  # maximum of 10 updates
                    GUILogger.info(f"Progress: {progString}.")
            i += 1
    else:  # We want to use parallel iteration if possible
        ts = yt.load(Param_Dict["Directory"] + "/" + Param_Dict["Seriesname"])
        for store, ds in ts.piter(storage=storage):
            if i % onlyEvery == 0:
                ad = ds.all_data()
                prof = yt.create_profile(ad, Param_Dict["XAxis"],
                                         fields=[Param_Dict["YAxis"]],
                                         weight_field=Param_Dict["WeightField"])
                # Add labels
                time = Param_Dict["DataSetDict"][str(ds) + "Time"]
                label = "{} at {:.3g} ".format(Param_Dict["YAxis"], time.value)
                label += str(time.units)
                labels.append(label)
                store.result = prof[Param_Dict["YAxis"]]
                progString = f"{int(i/onlyEvery+1)}/{length} profiles done"
                emitStatus(worker, progString)
                GUILogger.info(f"Progress: {progString}.")
            i += 1
    # Convert the storage dictionary values to an array with x-axis as first
    # row and then the results of y-field as following rows.
    arr_x = prof.x
    arr = [arr_x]
    for arr_y in storage.values():
        if arr_y is not None:
            arr.append(arr_y)
    return arr, labels


def createProfWithTimeForX(Param_Dict, worker):
    """Make a profile plot having the time as the x-Axis.
    Parameters:
        Param_Dict: For the fields and DataSets to be plotted.
    Returns:
        arr: list containing two YTArrays having the time as the first and the
             y-field as second entry
    """
    GUILogger.info("This may take some...time...")
    ts = Param_Dict["DataSeries"]
    timeMin = Param_Dict["XMin"]  # they should already be converted to xunit.
    timeMax = Param_Dict["XMax"]
    times = []
    datasets = []
    emitStatus(worker, "Gathering time data")
    for ds in ts:
        # use the times we have already calculated for each dataset
        time = Param_Dict["DataSetDict"][str(ds) + "Time"].to_value(Param_Dict["XUnit"])
        timecompare = float("{:.3g}".format(time))
        if timeMin <= timecompare <= timeMax:
            times.append(time)
            datasets.append(str(ds))
    GUILogger.log(29, "Iterating over the whole series from {:.3g} to {:.3g} {}..."
          .format(timeMin, timeMax, Param_Dict["XUnit"]))
    calcQuan = getCalcQuanName(Param_Dict)
    field = Param_Dict["YAxis"]
    calcQuanString = getCalcQuanString(Param_Dict)
    storage = {}
    i = 0
    length = len(times)
    if Param_Dict["YAxis"] in Param_Dict["NewDerFieldDict"].keys():
        for ds in ts:
            if str(ds) in datasets:
                try:
                    yResult = Param_Dict["DataSetDict"][str(ds) + field + calcQuan]
                except KeyError:
                    ad = ds.all_data()
                    yResult = eval(calcQuanString)
                    # save the plotpoints for later use
                    value = yt.YTQuantity(yResult, Param_Dict["YUnit"]).to_value(Param_Dict["FieldUnits"][field])
                    Param_Dict["DataSetDict"][str(ds) + field + calcQuan] = value
                storage[str(i)] = yResult  # this is kind of clunky, but this way we don't run into problems later
                i += 1
                progString = f"{i}/{length} data points calculated"
                emitStatus(worker, progString)
                if i % ceil(length/10) == 0:  # maximum of 10 updates
                    GUILogger.info(f"Progress: {progString}.")
    else:  # We want to use parallel iteration if possible
        yt.enable_parallelism(suppress_logging=True)
        newTS = yt.load(Param_Dict["Directory"] + "/" + Param_Dict["Seriesname"])
        for store, ds in newTS.piter(storage=storage):
            try:
                yResult = Param_Dict["DataSetDict"][str(ds) + field + calcQuan]
            except KeyError:
                ad = ds.all_data()  # This is needed for the following command
                yResult = eval(calcQuanString)
                # save the plotpoints for later use
                value = yt.YTQuantity(yResult, Param_Dict["YUnit"]).to_value(Param_Dict["FieldUnits"][field])
                Param_Dict["DataSetDict"][str(ds) + field + calcQuan] = value
            store.result = yResult
            i += 1
            progString = f"{i}/{length} data points calculated"
            emitStatus(worker, progString)
            if i % ceil(length/10) == 0:  # maximum of 10 updates
                GUILogger.info(f"Progress: {progString}.")
    labels = [field]
    # Convert the storage dictionary values to an array, so they can be
    # easily plotted
    arr_x = yt.YTArray(times, Param_Dict["XUnit"])
    arr_y = yt.YTArray(list(storage.values()), Param_Dict["YUnit"])
    arr = [arr_x, arr_y]
#    print(arr)
    return arr, labels


# %% Functions for setting the axis settings (general, and profile)
def setAxisSettings(plot, Param_Dict, Axis):
    """Performs a check on the minima and maxima of the given axis and sets
    the plot min/max, unit, log and if needed color scheme accordingly.
    Parameters:
        plot: yt plot object
        Param_Dict: Parameter Dictionary to get input
        Axis: field where the min/max has to be set
    """
    field = Param_Dict[Axis + "Axis"]
    if Param_Dict["DomainDiv"] and Param_Dict["PlotMode"] == "Projection":
        field = "Normed " + field
    fieldMin = Param_Dict[Axis + "Min"]  # Float
    fieldMax = Param_Dict[Axis + "Max"]
    log = Param_Dict[Axis + "Log"]  # Boolean
    if (fieldMin <= 0 or fieldMax <= 0) and log:
        # In the GUI it is prevented that phase, profile and line plot can set
        # an axis both logarithmic and with a negative min
        plot.set_log(field, Param_Dict[Axis + "Log"],
                     linthresh=((fieldMax-fieldMin)/1000))
    else:
        plot.set_log(field, log)
    plot.set_unit(field, Param_Dict[Axis + "Unit"])
    if Axis == "X":
        plot.set_xlim(fieldMin, fieldMax)
    if Axis == "Y":
        if Param_Dict["PlotMode"] == "Line":
            pass
        elif Param_Dict["PlotMode"] == "Profile":
            plot.set_ylim(field, fieldMin, fieldMax)
        else:
            plot.set_ylim(fieldMin, fieldMax)
    if Axis == "Z":
        plot.set_zlim(field, fieldMin, fieldMax)
    if Param_Dict["DimMode"] == "2D":
        # Change color scheme according to the one selected
        plot.set_cmap(field, Param_Dict["ColorScheme"])


def setProfileAxisSettings(Param_Dict, axis, axes):
    """Sets the axis settings for profile plots. This includes log scaling,
    limits and setting the labels to the correct latex representation.
    Parameters:
        Param_Dict: Parameter dictionary for dataset, axis and unit
        axis: "X" or "Y" for the axis
        axes: the axes instance to put the label on
    """
    if Param_Dict[axis + "Log"]:
        eval(f"axes.set_{axis.lower()}scale('log')")
    field = Param_Dict[axis + "Axis"]
    ds = Param_Dict["CurrentDataSet"]  # is necessary for eval commands
    unit = yt.YTQuantity(1, Param_Dict[axis + "Unit"]).units.latex_repr  # get latex repr for unit
    if unit != "":  # do not add empty brackets
        unit = r"$\:\left[" + unit + r"\right]$"
    if field == "dens" or field == "temp":
        name = eval(f"ds.fields.flash.{field}.get_latex_display_name()")
    elif field == "time":
        name = r"$\rm{Time}$"
    else:
        name = eval(f"ds.fields.gas.{field}.get_latex_display_name()")
    eval(f"axes.set_{axis.lower()}label(name + unit)")
    eval(f"axes.set_{axis.lower()}lim(Param_Dict[axis + 'Min'], Param_Dict[axis + 'Max'])")
