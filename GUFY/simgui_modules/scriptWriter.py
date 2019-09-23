# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

A script for writing plot scripts.

The module is structured as follows:
    - The WriteToScriptDialog class for the write-to-script options
    - Functions for saving the file and writing it
    - Functions for constructing the slice and projection plot strings
    - Functions for constructing the line and phase plot strings
    - Function for constructing the profile plot strings
          (All variants including time series)
    - Function for constructing the plot-making string
    - Functions to construct time series strings
    - Functions to construct miscellaneous strings like derived fields, file
          loading and annotations (alphabetical order)
"""
import PyQt5.QtWidgets as QW
import PyQt5.QtCore as QC
import PyQt5.QtGui as QG
from datetime import datetime
import math
import yt
from simgui_modules.utils import getCalcQuanName, getCalcQuanString
from simgui_modules.additionalWidgets import GUILogger
from simgui_modules.checkBoxes import coolCheckBox


# %% The WriteToScriptDialog class for the write-to-script options
class WriteToScriptDialog(QW.QDialog):
    """A dialog that pops up if the user wants to write the settings of the GUI
    or the plot to a reproducible script.
    Params:
        Param_Dict: For receiving information that has to be written to script
        PlotWindow: Whether the instance belongs to a plot window or the
                    general GUI
    """
    def __init__(self, Param_Dict, PlotWindow=True):
        super().__init__()
        if PlotWindow:
            GUILogger.info("Options for writing the plot displayed as a reproducible skript")
            self.setWindowTitle("Options for writing the plot to script")
            self.text = "that were used to create the plot"
        else:
            GUILogger.info("Options for writing settings of the GUI as a reproducible skript")
            self.setWindowTitle("Options for writing the settings to script")
            self.text = "of the GUI as they are specified in the <b>Plot options</b>"
        GUILogger.info("Detailed information for making plots using yt can "
                       "also be found "
                       '<a href="https://yt-project.org/doc/visualizing/plots.html">here</a>, '
                       '<a href="https://yt-project.org/doc/cookbook/simple_plots.html">here</a> and '
                       '<a href="https://yt-project.org/doc/cookbook/complex_plots.html">here</a>.')
        self.noComments = False
        self.plotAll = False
        self.Param_Dict = Param_Dict
        self.setModal(True)
        self.initUi(PlotWindow)
        self.signalsConnection()
        self.resize(400, 300)
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.show()

    def initUi(self, PlotWindow):
        """Initialize all of the ingredients for this UI."""
        # Buttons for closing the window:
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.addButton("Create script", QW.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QW.QDialogButtonBox.RejectRole)
        self.textBrowser = QW.QTextBrowser()
        text = ""
        if not PlotWindow:
            text += ("""<p><b><font color="red">Warning:</font></b> Due to the way
                     the script writing works, the script might be
                     incomplete concerning some of the extrema or other
                     settings. </p>""")
        text += f"""<p>If you want, I can now produce a script with the
        settings {self.text} for you. </p>
        <p>Pressing the <b>Create script</b>-button will prompt you
        to enter a filename of where the script is to be created.</p>
        <p>If you don't want comments in the script - which is understandable
        if you're experienced, for beginners they might be useful - just
        check the checkbox below.</p>"""
        self.commentCheckBox = coolCheckBox(text="Disable comments", width=None)
        layout = QW.QVBoxLayout()
        layout.addWidget(self.textBrowser)
        layout.addWidget(self.commentCheckBox)
        series = self.Param_Dict["isValidSeries"]
        noMultiple = not self.Param_Dict["TimeSeriesProf"]
        notTime = not self.Param_Dict["XAxis"] == "time"
        if series and noMultiple and notTime:
            text += """<p>Since you have loaded a time series, you may transfer
            the <b>Plot all</b> functionality to the script as well. Just tick
            the corresponding CheckBox"""
            self.makeSeriesCheckBox = coolCheckBox(text="Write script to plot all", width=None)
            self.makeSeriesCheckBox.toggled.connect(self.getSeriesInput)
            layout.addWidget(self.makeSeriesCheckBox)
        self.textBrowser.setHtml(text)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def signalsConnection(self):
        """Connects all the signals and emits some of them for a proper start
        """
        self.buttonBox.accepted.connect(self.applyPressed)
        self.buttonBox.rejected.connect(self.cancelPressed)
        self.commentCheckBox.toggled.connect(self.getCommentInput)
        self.accepted.connect(lambda: saveFile(self))

    def applyPressed(self):
        """Handles the Button Press of 'Create n plots'"""
        self.accept()

    def cancelPressed(self):
        """Handles the Button press of 'Cancel'"""
        self.reject()

    def getCommentInput(self, state):
        """Saves the state of the checkbox"""
        self.noComments = state

    def getSeriesInput(self, state):
        self.plotAll = state


# %% Functions for saving the file and writing it
def saveFile(dialog):
    """Ask the user to give a name for the file to be written out and save
    the plot with its current settings as a script."""
    filename = QW.QFileDialog.getSaveFileName(dialog, 'Write Plot to file',
                                              dialog.Param_Dict["Directory"],
                                              "Python files (*.py);; "
                                              "All files (*)")[0]
    if filename != "":
        writePlotToScript(dialog.Param_Dict, filename, dialog.noComments,
                          dialog.plotAll)
        GUILogger.log(29, "A script to reproduce the plot has been writt"
                      f"en to <b>{filename}</b>.")
    else:
        GUILogger.info("No filename selected.")


def writePlotToScript(Param_Dict, filename, noComments, plotAll):
    """Write the plot passed through Param_Dict to a file filename.
    Params:
        Param_Dict: Parameter dictionary containing all of the settings
        filename: Name of the file to be written (including directory)
        noComments: bool if the user doesn't want comments
        plotAll: For time series if the user wants to have iteration
    """
    if not filename.endswith(".py"):
        filename += ".py"
    text = constructCompleteString(Param_Dict, plotAll, filename)
    if noComments:
        textLines = text.split("\n")
        # remove all lines that begin with a hashtag:
        textLines = [line for line in textLines if not line.strip().startswith("#")]
        textLines.insert(0, "# -*- coding: utf-8 -*-")
        # remove all in-line-comments:
        text = ""
        for line in textLines:
            if "#" in line:
                text += line.split("  # ")[0]
            elif not line.isspace():  # check if all of the characters are spaces
                text += line
            text += "\n"
        # remove all 'Note:'-blocks:
        textBlocks = text.split('"""\nNote:')
        text = ""
        for i, block in enumerate(textBlocks):
            if i != 0:
                block = "".join(block.split('"""')[1:])
            text += block
    with open(filename, "w") as file:
        file.write(text)


# %% Function for writing the introduction
def constructCompleteString(Param_Dict, plotAll, filename):
    """Construct a long string that can be used to replot the plot with its
    current settings.
    Params:
        Param_Dict: Parameter dictionary containing all of the plot data
    Returns:
        text: String that can be used to replot the plot
    """
    introString = f'''# -*- coding: utf-8 -*-
"""
{filename.split("/")[-1]}
Script containing the plot produced using GUFY - GUI for FLASH Code simulations
based on yt.

Created on {datetime.now().strftime("%a, %b %d %X %Y")}.

Contains a suggestion to reproduce the plot(s).
Since it is dynamically created, it may not be the prettiest but I hope it can
help to get started.\n
If you detect any bugs or have questions, please contact me via email through
fabian.balzer@studium.uni-hamburg.de.
"""
import yt
import matplotlib.pyplot as plt
'''
    if Param_Dict["DimMode"] == "2D":
        introString += "from mpl_toolkits.axes_grid1 import make_axes_locatable\n"
    if plotAll:
        introString += "import os"
    introString += "\n\n"
    introString += constructDerFieldString(Param_Dict)
    if checkTimeSeriesPlot(Param_Dict, plotAll):
        plotString = constructSeriesString(Param_Dict, plotAll)
    elif Param_Dict["isValidFile"]:
        plotString = constructFileString(Param_Dict)
    else:
        return "# This shouldn't happen. Something went wrong writing the file"
    text = introString + plotString
    return text


def constructFileString(Param_Dict):
    """Constructs the string when handling a single file"""
    loadingString = "# Load the file through yt and save the dataset as ds:\n"
    loadingString += f'ds = yt.load("{Param_Dict["Directory"]}/{str(Param_Dict["CurrentDataSet"])}")\n\n'
    plotString = eval("construct"+Param_Dict["PlotMode"]+"Plot(Param_Dict)")
    text = loadingString + plotString
    return text


# %% Functions for constructing the slice and projection plot strings
def constructSlicePlot(Param_Dict):
    """Constructs the Slice plot script"""
    ds = Param_Dict["CurrentDataSet"]
    gridUnit = Param_Dict["GridUnit"]
    c0, c1, c2 = Param_Dict["XCenter"], Param_Dict["YCenter"], Param_Dict["ZCenter"]
    width = f'(({Param_Dict["HorWidth"]}, "{gridUnit}"), ({Param_Dict["VerWidth"]}, "{gridUnit}"))'
    field = Param_Dict["ZAxis"]
    if Param_Dict["NormVecMode"] == "Axis-Aligned":
        plotString = (
f'''
# Initialize a yt axis-aligned slice plot with the dataset ds, normal vector {Param_Dict["NAxis"]},
# field {field} and the optional parameters axes_unit, center, width and fontsize:
c0 = yt.YTQuantity({c0}, "{gridUnit}")  # Get the center coordinates.
c1 = yt.YTQuantity({c1}, "{gridUnit}")  # Unfortunately, using a YTArray
c2 = yt.YTQuantity({c2}, "{gridUnit}")  # does not work properly.
slc = yt.SlicePlot(ds, "{Param_Dict["NAxis"]}", "{field}", axes_unit="{gridUnit}",
                   center=[c0, c1, c2], width={width},
                   fontsize=14)
''')
    else:
        normVec = [Param_Dict[axis + "NormDir"] for axis in ["X", "Y", "Z"]]
        northVec = [Param_Dict[axis + "NormNorth"] for axis in ["X", "Y", "Z"]]
        plotString = (
f'''# Initialize a yt off-axis slice plot with the dataset ds, normal vector,
# field {field} and the optional parameters north_vector, axes_unit, center and
# fontsize. The north vector is the vector that defines the 'up'-direction:
c0 = yt.YTQuantity({c0}, "{gridUnit}")  # Get the center coordinates.
c1 = yt.YTQuantity({c1}, "{gridUnit}")  # Unfortunately, using a YTArray
c2 = yt.YTQuantity({c2}, "{gridUnit}")  # does not work properly.
slc = yt.OffAxisSlicePlot(ds, {normVec}, "{field}", north_vector={northVec},
                          axes_unit="{gridUnit}", fontsize=14, center=[c0, c1, c2])
''')
    plotString += f'# Hint: You can access the generated data using slc.frb["{field}"]\n\n\n'
    modString = ""
    fieldMin = Param_Dict["ZMin"]  # Float
    fieldMax = Param_Dict["ZMax"]
    if field not in Param_Dict["FieldMins"].keys():
        modString = (
f'''# It seems that you have not calculated extrema for {field}.
# You can do this by using
# minMaxArray = ds.all_data().quantities.extrema({field})
# which will return a YTArray with two entries plus the units.
''')
    unit = Param_Dict["ZUnit"]
    cmap = Param_Dict["ColorScheme"]
    modString += ("# Set unit, minimum, maximum and color scheme:\n"
                 'slc.set_unit("{0}", "{1}")\nslc.set_zlim("{0}", {2}, {3})  '
                 '# These are given in the same unit, {1}.\n'
                 'slc.set_cmap("{0}", "{4}")\n'.format(field, unit, fieldMin, fieldMax, cmap))
    log = Param_Dict["ZLog"]  # Boolean
    if fieldMin != "":
        modString += "# Set our field scaling logarithmic if wanted:\n"
        if min(fieldMin, fieldMax) <= 0 and log:
            modString += ('slc.set_log("{0}", True, linthresh=(({1}-{2})/1000))  '
            "# linthresh sets a linear scale for a small portion and then a symbolic one "
            "for negative values\n".format(field, fieldMax, fieldMin))
        else:
            modString += f'slc.set_log("{field}", {log})  # This may be redundant in some cases\n'
    zoom = Param_Dict["Zoom"]
    modString += f"slc.zoom({zoom})\n\n\n"

    # Do the annotations:
    annoString = ""
    title = Param_Dict["PlotTitle"]
    if title != "":
        annoString += f'slc.annotate_title("{title}")  # Give the plot the title it deserves.\n'
    if Param_Dict["Timestamp"]:
        annoString += ("slc.annotate_timestamp(corner='upper_left', draw_inset_box=Tr"
        "ue)  # There are many more modifications for the timestamp.\n")
    if Param_Dict["Geometry"] == "cartesian":
        if Param_Dict["Scale"]:
            annoString += "slc.annotate_scale(corner='upper_right')\n"
        if Param_Dict["Grid"]:
            annoString += ('WARNING = "There is a yt-internal bug where grid '
                          'annotation doesn\'t work if a center coordinate is '
                          'set to 0!"\nslc.annotate_grids()\n')
        if Param_Dict["ParticleAnno"]:
            if Param_Dict["PSlabWidth"] == "" or float(Param_Dict["PSlabWidth"]) == 0:
                Param_Dict["PSlabWidth"] = 1
            height = abs(Param_Dict["FieldMins"]["DomainHeight"] - Param_Dict["FieldMaxs"]["DomainHeight"])
            width = float(Param_Dict["PSlabWidth"])*height
            annoString += (f"slc.annotate_particles({width})\n")
        if Param_Dict["VelVectors"]:
            annoString += "slc.annotate_velocity(normalize=True)\n"
        if Param_Dict["VelStreamlines"]:
            annoString += ('WARNING = "There is a yt-internal bug where streamline '
                          'annotation doesn\'t work if a center coordinate is '
                          'set to 0!"\n')
            if Param_Dict["NAxis"] == "x":
                annoString += "slc.annotate_streamlines('velocity_y', 'velocity_z')\n"
            elif Param_Dict["NAxis"] == "y":
                annoString += "slc.annotate_streamlines('velocity_x', 'velocity_z')\n"
            elif Param_Dict["NAxis"] == "z":
                annoString += "slc.annotate_streamlines('velocity_x', 'velocity_y')\n"
        if Param_Dict["MagVectors"]:
            annoString += "slc.annotate_magnetic_field(normalize=True)\n"
        if Param_Dict["MagStreamlines"]:
            annoString += ('WARNING = "There is a yt-internal bug where streamline '
                          'annotation doesn\'t work if a center coordinate is '
                          'set to 0!"\n')
            if Param_Dict["NAxis"] == "x":
                annoString += "slc.annotate_streamlines('magy', 'magz')\n"
            elif Param_Dict["NAxis"] == "y":
                annoString += "slc.annotate_streamlines('magx', 'magz')\n"
            elif Param_Dict["NAxis"] == "z":
                annoString += "slc.annotate_streamlines('magx', 'magy')\n"
        if Param_Dict["Contour"]:
            annoString += "slc.annotate_contour('{}')\n".format(field)
    elif Param_Dict["Geometry"] == "cylindrical":
        if Param_Dict["Grid"]:
            annoString += "slc.annotate_grids()\n"
    if len(annoString) > 0:  # If annotations are made, declare them:
        annoString = "# Annotations for the plot:\n" + annoString + "\n\n"
    figureString = constructUsingMPL(Param_Dict, "slc")

    text = plotString + modString + annoString + figureString
    return text


def constructProjectionPlot(Param_Dict):
    """Constructs the projection plot script"""
    ds = Param_Dict["CurrentDataSet"]
    field = Param_Dict["ZAxis"]
    if Param_Dict["WeightField"] is None:
        weightField = "None"
    else:
        weightField = '"{}"'.format(Param_Dict["WeightField"])
    plotString = ""
    if Param_Dict["DomainDiv"]:
        # in case the user wants to divide everything by the domain_height,
        # we define a new field which is just the old field divided by height
        # and then do a projectionPlot for that.
        height = Param_Dict["FieldMaxs"]["DomainHeight"] - Param_Dict["FieldMins"]["DomainHeight"]
        plotString += (
f"""# We want to norm our projection by the domain height:
domainHeight = {height}  # You can obtain this by calculating 
# ds.domain_right_edge - ds.domain_left_edge for all dimensions
# To do this, we can define a new field for the dataset:
def _NormField(field, data):
    return data["{field}"]/yt.units.YTQuantity(ds.arr(domainHeight, "code_length"))  # This way, yt will understand the units
""")
        field = "Normed " + field
        plotString += f'unit = yt.units.unit_object.Unit("{Param_Dict["ZUnit"]}/cm")'
        plotString += ("# Unfortunately add_field doesn't understand lambda functions.\n"
                       'ds.add_field(("gas", "{field}"), function=_NormField,\n'
                       "             units='auto', dimensions=unit.dimensions)\n\n\n")
    NVector, gridUnit = Param_Dict["NAxis"], Param_Dict["GridUnit"]
    c0, c1, c2 = Param_Dict["XCenter"], Param_Dict["YCenter"], Param_Dict["ZCenter"]
    width = f'(({Param_Dict["HorWidth"]}, "{gridUnit}"), ({Param_Dict["VerWidth"]}, "{gridUnit}"))'
    field = Param_Dict["ZAxis"]
    if Param_Dict["ParticlePlot"]:
        plotString += (
f'''
# Initialize a yt Particle Projection plot with the dataSet ds, Normal
# Vector {NVector}, field {field} and the optional parameters axes_unit,
# weight_field, center and fontsize:
c0 = yt.YTQuantity({c0}, "{gridUnit}")  # Get the center coordinates.
c1 = yt.YTQuantity({c1}, "{gridUnit}")  # Unfortunately, using a YTArray
c2 = yt.YTQuantity({c2}, "{gridUnit}")  # does not work properly.
proj = yt.ParticleProjectionPlot(ds, "{Param_Dict["NAxis"]}", "{field}",
                                 axes_unit="{gridUnit}", center=[c0, c1, c2],
                                 weight_field={weightField}, width={width},
                                 fontsize=14)
# Warning: Particle plots are still an experimental feature of the GUI and may
# produce errors
''')
    elif Param_Dict["NormVecMode"] == "Axis-Aligned":
        plotString += (
f'''
# Initialize a yt Projection plot with the dataSet ds, Normal Vector {NVector},
# field {field} and the optional parameters axes_unit, weight_field,
# center and fontsize:
c0 = yt.YTQuantity({c0}, "{gridUnit}")  # Get the center coordinates.
c1 = yt.YTQuantity({c1}, "{gridUnit}")  # Unfortunately, using a YTArray
c2 = yt.YTQuantity({c2}, "{gridUnit}")  # does not work properly.
proj = yt.ProjectionPlot(ds, "{Param_Dict["NAxis"]}", "{field}", axes_unit="{gridUnit}",
                         center=[c0, c1, c2], weight_field={weightField},
                         width={width}, fontsize=14)
''')
    else:
        normVec = [Param_Dict[axis + "NormDir"] for axis in ["X", "Y", "Z"]]
        northVec = [Param_Dict[axis + "NormNorth"] for axis in ["X", "Y", "Z"]]
        plotString += (
f'''
# Initialize a yt Projection plot with the dataSet ds, Normal Vector {NVector},
# field {field} and the optional parameters axes_unit, weight_field,
# center and fontsize:
c0 = yt.YTQuantity({c0}, "{gridUnit}")  # Get the center coordinates.
c1 = yt.YTQuantity({c1}, "{gridUnit}")  # Unfortunately, using a YTArray
c2 = yt.YTQuantity({c2}, "{gridUnit}")  # does not work properly.
proj = yt.OffAxisProjectionPlot(ds, {normVec}, "{field}", north_vector={northVec},
                                axes_unit="{gridUnit}", center=[c0, c1, c2],
                                weight_field={weightField}, width={width},
                                fontsize=14)
''')
    plotString += f'# Hint: You can access the generated data using proj.frb["{field}"]\n\n\n'
    modString = ""
    fieldMin = Param_Dict["ZMin"]  # Float
    fieldMax = Param_Dict["ZMax"]
    if field not in Param_Dict["FieldMins"].keys():
        modString = (
f'''# It seems that you have not calculated extrema for {field}.
# You can do this by using
# minMaxArray = ds.all_data().quantities.extrema({field})
# which will return a YTArray with two entries plus the units.
''')
    unit = Param_Dict["ZUnit"]
    cmap = Param_Dict["ColorScheme"]
    modString += ("# Set unit, minimum, maximum and color scheme:\n"
                 'proj.set_unit("{0}", "{1}")\nproj.set_zlim("{0}", {2}, {3})  '
                 '# These are given in the same unit, {1}.\n'
                 'proj.set_cmap("{0}", "{4}")\n'.format(field, unit, fieldMin, fieldMax, cmap))
    if fieldMin == "":
        log = Param_Dict["ZLog"]  # Boolean
        modString += "# Set our field scaling logarithmic if wanted:\n"
        if min(fieldMin, fieldMax) <= 0 and log:
            modString += ("proj.set_log('{0}', True, linthresh=(({1}-{2})/1000)  "
            "# linthresh sets a linear scale for a small portion and then a symbolic one "
            "for negative values\n".format(field, fieldMax, fieldMin))
        else:
            modString += f'proj.set_log("{field}", {log})  # This may be redundant in some cases.\n'
    zoom = Param_Dict["Zoom"]
    modString += f"proj.zoom({zoom})\n\n"
    # Do the annotations:
    annoString = ""
    title = Param_Dict["PlotTitle"]
    if title != "":
        annoString += f'proj.annotate_title("{title}")  # Give the plot the title it deserves.\n'
    if Param_Dict["Timestamp"]:
        annoString += ("proj.annotate_timestamp(corner='upper_left', draw_inset_box=Tr"
        "ue)  # There are many more modifications for the timestamp.\n")
    if Param_Dict["Geometry"] == "cartesian":
        if Param_Dict["Scale"]:
            annoString += "proj.annotate_scale(corner='upper_right')\n"
        if Param_Dict["Grid"]:
            annoString += ('WARNING = "There is a yt-internal bug where grid '
                          'annotation doesn\'t work if a center coordinate is '
                          'set to 0!"\n')
            annoString += "proj.annotate_grids()\n"
        if Param_Dict["ParticleAnno"]:
            if Param_Dict["PSlabWidth"] == "" or float(Param_Dict["PSlabWidth"]) == 0:
                Param_Dict["PSlabWidth"] = 1
            height = abs(Param_Dict["FieldMins"]["DomainHeight"] - Param_Dict["FieldMaxs"]["DomainHeight"])
            width = float(Param_Dict["PSlabWidth"])*height
            annoString += (f"slc.annotate_particles({width})\n")
        if Param_Dict["VelVectors"]:
            annoString += "proj.annotate_velocity(normalize=True)\n"
        if Param_Dict["VelStreamlines"]:
            annoString += ('WARNING = "There is a yt-internal bug where streamline '
                          'annotation doesn\'t work if a center coordinate is '
                          'set to 0!"\n')
            if Param_Dict["NAxis"] == "x":
                annoString += "proj.annotate_streamlines('velocity_y', 'velocity_z')\n"
            elif Param_Dict["NAxis"] == "y":
                annoString += "proj.annotate_streamlines('velocity_x', 'velocity_z')\n"
            elif Param_Dict["NAxis"] == "z":
                annoString += "proj.annotate_streamlines('velocity_x', 'velocity_y')\n"
        if Param_Dict["MagVectors"]:
            annoString += "proj.annotate_magnetic_field(normalize=True)\n"
        if Param_Dict["MagStreamlines"]:
            annoString += ('WARNING = "There is a yt-internal bug where streamline '
                          'annotation doesn\'t work if a center coordinate is '
                          'set to 0!"\n')
            if Param_Dict["NAxis"] == "x":
                annoString += "proj.annotate_streamlines('magy', 'magz')\n"
            elif Param_Dict["NAxis"] == "y":
                annoString += "proj.annotate_streamlines('magx', 'magz')\n"
            elif Param_Dict["NAxis"] == "z":
                annoString += "proj.annotate_streamlines('magx', 'magy')\n"
        if Param_Dict["Contour"]:
            annoString += "proj.annotate_contour('{}')\n".format(field)
    elif Param_Dict["Geometry"] == "cylindrical":
        if Param_Dict["Grid"]:
            annoString += "proj.annotate_grids()\n"
    annoString += "\n"
    figureString = constructUsingMPL(Param_Dict, "proj")

    text = plotString + modString + annoString + figureString
    return text


# %% Functions for constructing the line and phase plot strings
def constructLinePlot(Param_Dict):
    """Constructs the line plot script"""
    ds = Param_Dict["CurrentDataSet"]
    startends = ["XLStart", "YLStart", "ZLStart", "XLEnd", "YLEnd", "ZLEnd"]
    valueList = []
    for key in startends:
        value = float(yt.units.YTQuantity(Param_Dict[key], Param_Dict["oldGridUnit"]).to(ds.quan(1, 'code_length').units).value)
        valueList.append(value)
    field = Param_Dict["YAxis"]
    plotString = (
f"""# Initialize a yt Line plot with the dataSet ds, field {field}, the
# given start- and end points in code_length and the number of sampling points:
lplot = yt.LinePlot(ds, "{field}", {valueList[:3]}, {valueList[3:]},
                    npoints=512, fontsize=14)
""")
    plotString += ("# Note that you can also add more than one field for the "
                   "line plot and that you\n# can label them independently "
                   'using field_labels={"field":label}.\n\n')
    modString = (f'lplot.annotate_legend("{field}")  # Optional, but looks nice\n')
    fieldMin = Param_Dict["YMin"]  # Float
    fieldMax = Param_Dict["YMax"]
    unit = Param_Dict["ZUnit"]
    modString += f'lplot.set_x_unit("{Param_Dict["LineUnit"]}")\n'
    modString += f'lplot.set_unit("{field}", "{unit}")\n'
    modString += ("# Unfortunately, yt line-plots don't have built in min and "
                  "max settings, so we use pyplot later.\n")
    log = Param_Dict["ZLog"]  # Boolean
    modString += "# Set our field scaling logarithmic if wanted:\n"
    if min(fieldMin, fieldMax) <= 0 and log:
        modString += (f'lplot.set_log("{field}", True, linthresh=(({fieldMax}-{fieldMin})/1000)  '
        "# linthresh sets a linear scale for a small portion and then a symbolic one "
        "for negative values\n")
    else:
        modString += (f'lplot.set_log("{field}", {log})  # This may be redundant '
                      "in some cases.\n")
    annoString = ""
    title = Param_Dict["PlotTitle"]
    if title != "":
        annoString += (f'lplot.annotate_title("{Param_Dict["YAxis"]}", "{title}")'
                       "#  Give the plot the title it deserves.\n")
    figureString = constructUsingMPL(Param_Dict, "lplot")

    text = plotString + modString + annoString + figureString
    return text


def constructPhasePlot(Param_Dict):
    """Constructs the phase plot script"""
    XField, YField, ZField = Param_Dict["XAxis"], Param_Dict["YAxis"], Param_Dict["ZAxis"]
    plotString = ("ad = ds.all_data()  # through e.g. ad = ds.sphere('c', (50, 'kpc"
                  "')) you could also only select a region of the dataset.\n\n")
    if Param_Dict["WeightField"] is None:
        weightField = "None"
    else:
        weightField = f'"{Param_Dict["WeightField"]}"'
    plotString += (
f"""# Initialize a yt phase plot with the data ad, XField {XField},
# YField {YField}, ZField {ZField} and the optional parameters 
# weight_field, fractional, the number of bins and fontsize:
""")
    if Param_Dict["ParticlePlot"]:
        plotString += (
f'''phas = yt.ParticlePhasePlot(ad, "{XField}", "{YField}", "{ZField}",
                            weight_field={weightField}, x_bins=128, y_bins=128,
                            fontsize=14)
# Warning: Particle plots are still an experimental feature of the GUI and may
# produce errors


''')
    else:
        plotString += (
f'''phas = yt.PhasePlot(ad, "{XField}", "{YField}", "{ZField}",
                    weight_field={weightField}, fontsize=14)


''')
    cmap = Param_Dict["ColorScheme"]
    modString = ("# Set our field scaling logarithmic if wanted. "
                 "Phase plots don't support symlog scales.\n")
    for axis in ["X", "Y", "Z"]:
        log = Param_Dict[axis + "Log"]  # Boolean
        field = Param_Dict[axis + "Axis"]
        modString += f'phas.set_log("{field}", {log})  # This may be redundant in some cases.\n'
    modString += "# Set unit, minimum, maximum and color scheme:\n"
    for axis in ["X", "Y", "Z"]:
        modString += (f'phas.set_unit("{Param_Dict[axis +"Axis"]}", "{Param_Dict[axis + "Unit"]}")\n')
    if XField not in Param_Dict["FieldMins"].keys():
        modString += (
f'''# It seems that you have not calculated extrema for {XField}.
# You can do this by using
# minMaxArray = ds.all_data().quantities.extrema({XField})
# which will return a YTArray with two entries plus the units.
''')
    if YField not in Param_Dict["FieldMins"].keys():
        modString += (
f'''# It seems that you have not calculated extrema for {YField}.
# You can do this by using
# minMaxArray = ds.all_data().quantities.extrema({YField})
# which will return a YTArray with two entries plus the units.
''')
    if ZField not in Param_Dict["FieldMins"].keys():
        modString += (
f'''# It seems that you have not calculated extrema for {ZField}.
# You can do this by using
# minMaxArray = ds.all_data().quantities.extrema({ZField})
# which will return a YTArray with two entries plus the units.
''')
    XMin = Param_Dict["XMin"]
    XMax = Param_Dict["XMax"]
    YMin = Param_Dict["YMin"]
    YMax = Param_Dict["YMax"]
    ZMin = Param_Dict["ZMin"]
    ZMax = Param_Dict["ZMax"]
    modString += (f'phas.set_xlim({XMin}, {XMax})\n'
                  f'phas.set_ylim({YMin}, {YMax})\n'
                  f'phas.set_zlim("{ZField}", {ZMin}, {ZMax})  # These are given in the same unit, {Param_Dict["ZUnit"]}.\n')
    modString += f'phas.set_cmap("{ZField}", "{cmap}")\n'
    annoString = ""
    title = Param_Dict["PlotTitle"]
    if title != "":
        annoString += (f'phas.annotate_title("{Param_Dict["YAxis"]}", "{title}")'
                       "#  Give the plot the title it deserves.\n")
    figureString = constructUsingMPL(Param_Dict, "phas")

    text = plotString + modString + annoString + figureString
    return text


# %% Function for constructing the profile plot strings
# (All variants including time series)
def constructProfilePlot(Param_Dict, time=False, multiPlot=False):
    """Constructs the Profile plot script.
    Params:
        time: bool to indicate whether 'time' has been used for the x-axis
        multiPlot: bool to indicate whether the user wants to do plots at
                   multiple times
    """
    if Param_Dict["WeightField"] is None:
        weightField = "None"
    else:
        weightField = "'{}'".format(Param_Dict["WeightField"])
    ds = Param_Dict["CurrentDataSet"]
    if time:
        if weightField == "None":
            weightField = "'ones'"
        calcQuanName = getCalcQuanName(Param_Dict)
        calcQuanString = getCalcQuanString(Param_Dict).replace("'", '"')
        dataString = (
f'''# Loop over the datasets of the series to get the datapoints at each time:
# This does NOT reflect the extrema you chose in the GUI, please
# add them by hand by only using ts[start:(end+1)]
i = 0
time_data = []
y_data = []
length = len(ts)
for ds in ts:
    time_data.append(ds.current_time.to_value("{Param_Dict["XUnit"]}"))
    ad = ds.all_data()  # You could select an arbitrary yt region here
    # for available quantities to calculate see
    # https://yt-project.org/doc/analyzing/objects.html as well.
    yResult = {calcQuanString}
    y_data.append(yResult)
    i += 1
    print(f"Progress: {{i}}/{{length}} data points calculated.")
arr_x = yt.YTArray(time_data, "{Param_Dict["XUnit"]}")  # In a YTArray, the units
arr_y = yt.YTArray(y_data, "{Param_Dict["YUnit"]}")  # are stored as well.
"""
Note: Another way to do this is loading the series through yt using
ts = yt.load("{Param_Dict["Directory"]}/{Param_Dict["Seriesname"]}")
and then using the built-in parallel iteration tool, piter, like this:
yt.enable_parallelism(suppress_logging=True)
storage = {{}}  # A storage dictionary to store the data during parallel iteration
for store, ds in ts.piter(storage=storage):
    ad = ds.all_data()
    yResult = {calcQuanString}
    store.result = yResult
    i += 1
    print(f"Progress: {{i}}/{{length}} data points calculated."
y_arr = yt.YTArray(list(storage.values()), "{Param_Dict["YUnit"]}")
"""
''')
        # If possible, pass the values that have already been calculated to the user
        times, values = [], []
        field = Param_Dict["YAxis"]
        for ds in Param_Dict["DataSeries"]:
            try:
                time = Param_Dict["DataSetDict"][str(ds) + "Time"].to_value(Param_Dict["XUnit"])
                value = Param_Dict["DataSetDict"][str(ds) + field + calcQuanName]
                value = yt.YTQuantity(value, Param_Dict["FieldUnits"][field]).to_value(Param_Dict["YUnit"])
                times.append(time)
                values.append(value)
            except KeyError:
                pass
        if len(times) > 0:
            dataString += (
f'''# It seems that you have already calculated some plot points using the GUI.
# I have stored them for you, and you can reuse them if wanted:
calcTimes = yt.YTArray({times}, "{Param_Dict["XUnit"]}")
calcValues = yt.YTArray({values}, "{Param_Dict["YUnit"]}")


''')
    elif multiPlot:
        onlyEvery = Param_Dict["ProfOfEvery"]
        suf = lambda n: "%d%s "%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
        numString = suf(onlyEvery)
        dataString = (
f'''# Loop over the datasets of the series to make a profile at each time:
i = 0
onlyEvery = {onlyEvery}  # If you only want to plot every {numString} plot
length = {math.ceil(len(Param_Dict["DataSeries"])/onlyEvery)}  # You can use math.ceil(len(ts)/onlyEvery) to calculate this.
labels = []
profiles = []  # The data for the y-axis will be stored in YTArrays
for ds in ts:
    if i % onlyEvery == 0:
        # Create a data container to hold the whole dataset.
        ad = ds.all_data()  # you can use an arbitrary yt region here.
        # Create a 1d profile of xfield vs. yfield. Through n_bins the number
        # of bins may be modified as well:
        prof = yt.create_profile(ad, "{Param_Dict["XAxis"]}",
                                 fields=["{Param_Dict["YAxis"]}"],
                                 weight_field={weightField}, n_bins=64)
        # Add labels
        time = ds.current_time.to_value("kyr")
        label = f"{Param_Dict["YAxis"]} at {{time:.2e}} kyr"
        labels.append(label)
        profiles.append(prof["{Param_Dict["YAxis"]}"])
        print(f"Progress: {{int(i/onlyEvery)+1}}/{{length}} profiles done.")
    i += 1
arr_x = prof.x  # get the data for the x-axis
"""
Note: Another way to do this is loading the series through yt using
ts = yt.load("{Param_Dict["Directory"]}/{Param_Dict["Seriesname"]}")
and then using the built-in parallel iteration tool, piter, like this:
yt.enable_parallelism(suppress_logging=True)
storage = {{}}  # A storage dictionary to store the data during parallel iteration
for store, ds in ts.piter(storage=storage):
    if i % onlyEvery == 0:
        ad = ds.all_data()
        prof = yt.create_profile(ad, "{Param_Dict["XAxis"]}",
                                 fields=["{Param_Dict["YAxis"]}"],
                                 weight_field={weightField}, n_bins=64)
        # Add labels
        time = ds.current_time.to_value("kyr")
        label = f"{Param_Dict["YAxis"]} at {{time:.2e}} kyr"
        labels.append(label)
        store.result = prof["{Param_Dict["YAxis"]}"]
        print("Progress: {{int(i/onlyEvery+1}}/{{length}} profiles done."
    i += 1
arr_y = list(storage.values())
"""
''')
    else:
        dataString = (
f'''# First reate a data container to hold the whole dataset.
ad = ds.all_data()  # you can use an arbitrary yt region here.
# Create a 1d profile of the x-field vs. the y-field. You could also pass
# multiple fields for the vertical axis.
prof = yt.create_profile(ad, "{Param_Dict["XAxis"]}",
                         fields=["{Param_Dict["YAxis"]}"],
                         weight_field={weightField})
label = "{Param_Dict["YAxis"]}"
arr_x = prof.x
arr_y = prof["{Param_Dict["YAxis"]}"]


''')
    figureString = (
f'''# Now that we have created the data, we can set up a figure and plot it.
# More information: https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.pyplot.figure.html
fig, axes = plt.subplots(**{{'figsize': (10, 7), 'dpi': 100}})


# Add the plot:
x_values = arr_x.to_value("{Param_Dict["XUnit"]}")
''')
    if multiPlot:
        plotString = (
f'''for i, arr_y in enumerate(profiles):
    label = labels[i]
    y_values = arr_y.to_value("{Param_Dict["YUnit"]}")
    axes.plot(x_values, y_values, "-", linewidth=3, label=label)
''')
    else:
        plotString = (f'y_values = arr_y.to_value("{Param_Dict["YUnit"]}")\n'
                      f'axes.plot(x_values, y_values, "-", linewidth=3, label="{Param_Dict["YAxis"]}")\n')
    field = Param_Dict['XAxis']
    xUnit = yt.YTQuantity(1, Param_Dict["XUnit"]).units.latex_repr  # get latex repr for unit
    if xUnit != "":  # do not add empty brackets
        xUnit = r"$\:\left[" + xUnit + r"\right]$"
    if field == "dens" or field == "temp":
        xName = eval(f"ds.fields.flash.{field}.get_latex_display_name()")
    elif field == "time":
        xName = r"$\rm{Time}$"
    else:
        xName = eval(f"ds.fields.gas.{field}.get_latex_display_name()")
    field = Param_Dict["YAxis"]
    yUnit = yt.YTQuantity(1, Param_Dict["YUnit"]).units.latex_repr  # get latex repr for unit
    if yUnit != "":  # do not add empty brackets
        yUnit = r"$\:\left[" + yUnit + r"\right]$"
    if field == "dens" or field == "temp":
        yName = eval(f"ds.fields.flash.{field}.get_latex_display_name()")
    elif field == "time":
        yName = r"$\rm{Time}$"
    else:
        yName = eval(f"ds.fields.gas.{field}.get_latex_display_name()")
    if time:
        plotString += (
f'''
"""
Note:
Since you might not want to recalculate all the data, you can save the values
in a csv-file the following way:
import csv
with open("time_profile_{calcQuanName}_{field}_data.csv", "w") as writefile:
    # configure writer to write standard csv file
    writer = csv.writer(writefile, delimiter=',', lineterminator='\\n')
    writer.writerow(["time", "{field}"])
    writer.writerow(["{Param_Dict["XUnit"]}", "{Param_Dict["YUnit"]}"])
    for time, y in zip(time_data, y_data):
        writer.writerow([time, y])
    print("The data points have been saved to\\n"
          "time_profile_{calcQuanName}_{field}_data.csv.")
"""


''')
    elif multiPlot:
        pass
    else:
        plotString +=(
f'''
"""
Note:
Since you might not want to recalculate all the data, you can save the values
in a csv-file the following way:
import csv
with open("profile_{Param_Dict["XAxis"]}_{Param_Dict["YAxis"]}_data.csv", "w") as writefile:
    # configure writer to write standard csv file
    writer = csv.writer(writefile, delimiter=',', lineterminator='\\n')
    writer.writerow(["{Param_Dict["XAxis"]}", "{Param_Dict["YAxis"]}"])
    writer.writerow(["{Param_Dict["XUnit"]}", "{Param_Dict["YUnit"]}"])
    for time, y in zip(time_data, y_data):
        writer.writerow([time, y])
    print("The data points have been saved to\\n"
          "profile_{Param_Dict["XAxis"]}_{Param_Dict["YAxis"]}_data.csv.")
"""


''')
    plotString += (
'''
"""
Note:
We could also use yt's built-in yt.ProfilePlot.from_profiles(profiles, labels),
but we're using matplotlib.pyplot since it offers more control.
"""
# Modify the settings for x- and y-axis:
# with axes.set_xscale you can set it log(arithmic) or lin(ear).
''')
    if Param_Dict["XLog"]:
        plotString += 'axes.set_xscale("log")\n'
    if Param_Dict["YLog"]:
        plotString += 'axes.set_yscale("log")\n'
    plotString += (
f'''# We can freely customize the axes' names. You can get a units' LaTeX rep
# like this: yt.YTQuantity(1, "yourUnit").units.latex_repr
# and the display name with ds.fields.gas.YOURFIELD.get_latex_display_name()
axes.set_xlabel(r"{xName + xUnit}")
axes.set_ylabel(r"{yName + yUnit}")
axes.set_xlim({Param_Dict["XMin"]}, {Param_Dict["XMax"]})  # be careful about the units here
axes.set_ylim({Param_Dict["YMin"]}, {Param_Dict["YMax"]})
axes.legend()  # Display the labels we have given
axes.grid()  # You can customize the grid even further if wanted
axes.set_title(r"{Param_Dict["PlotTitle"]}")
''')
    if Param_Dict["AddProfile"]:
        plotString += (
'''
"WARNING: The second profile functionality is not a feature yet."
"""
Note: I have not implemented adding a second plot to this script writer yet.
It's actually pretty simple. Just use
twinaxes = axes.twinx()
twinaxes.tick_params(axis='y')
axes.tick_params(axis='y')
and plot the desired data on the twinaxes, which is going to use the same
x-axis.
"""
''')
    if Param_Dict["Timestamp"] and Param_Dict["XAxis"] != "time" and not multiPlot:
        plotString += ("# Use a custom function to annotate the timestamp (see above):\n"
                       "drawTimestampBox(axes, ds)\n")
    plotString += "# fig.show()  # Works best in iPython console or jupyter\n\n\n"
    saveString = '# example of how you could name the file:\n'
    saveString += f'plotfilename = "{str(Param_Dict["CurrentDataSet"])}_'
    if multiPlot:
        saveString += 'Multi'
    saveString += f'{Param_Dict["PlotMode"]}plot_{Param_Dict["YAxis"]}.png"\n'
    saveString += "fig.savefig(plotfilename)  # Takes the name of the file as an argument.\n"
    saveString += 'print(f"The file has been saved as {plotfilename}")\n'
    text = dataString + figureString + plotString + saveString
    if Param_Dict["Timestamp"] and Param_Dict["XAxis"] != "time" and not multiPlot:
        text = createCustomTimestampString() + text
    return text


# %% Function for constructing the plot-making string
def constructUsingMPL(Param_Dict, plotName):
    """Construct the part of the script where the yt plot is plotted as a mpl
    figure.
    params:
        Param_Dict: for retrieving information about what to plot
        plotName: the name the plot has been given, e.g. 'slc' for slice
    returns:
        text: constructed script text
    """
    mode = Param_Dict["PlotMode"]
    plotString = ("# Everything that's necessary for setting up the figure.\n"
                  "# More information: https://matplotlib.org/3.1.0/api/_as_gen/matplotlib.pyplot.figure.html\n"
                  'fig, axes = plt.subplots(**{"figsize": (10, 7), "dpi": 100})\n')
    if Param_Dict["DimMode"] == "2D":
        plotString += ("# Since we're using the color axis, we need the following:\n"
                       "divider = make_axes_locatable(axes)\n"
                       'cax = divider.append_axes("right", size="5%", pad=0.05)\n')
    plotString += ("\n\n# Now we need to pass our axes to yt so it can setup the"
                   " plots for us.\n")
    if mode == "Line":
        field = Param_Dict["YAxis"]
        plotString += f'{plotName}.plots["{field}"].axes = axes\n'
    else:
        field = Param_Dict["ZAxis"]
        if Param_Dict["DomainDiv"]:
            field = "Normed " + field
        plotString += f'{plotName}.plots["{field}"].axes = axes\n'
    if Param_Dict["DimMode"] == "2D":
        plotString += f'{plotName}.plots["{field}"].cax = cax\n'
    plotString += ("{0}._setup_plots()  # This runs the yt-internal command for"
                   " plotting. It's different for each plot type.\n".format(plotName))
    if mode == "Line":
        plotString += "axes.set_ylim({0}, {1})\n".format(Param_Dict["YMin"], Param_Dict["YMax"])
        if Param_Dict["LineAnno"]:
            plotString += "annotateStartEnd(axes, ds)  # annotate custom start and end points\n"
    if Param_Dict["Timestamp"] and mode in ["Line", "Phase"]:
        plotString += ("# Use a custom function to annotate the timestamp (see below):\n"
                       "drawTimestampBox(axes, ds)\n")
    if mode in ["Slice", "Projection"]:
        if Param_Dict["SetAspect"]:
            plotString += '# Set the aspect ratio. If "1", equal distances will be equally long.\n'
            plotString += 'axes.set_aspect("auto")  # For "auto", the figure is filled.\n'
    plotString += "# fig.show()  # Works best in iPython console or jupyter\n\n"
    saveString = ('\nplotfilename = "{0}_{1}plot_{2}.png"  # example of how you could name the file\n'
                 .format(str(Param_Dict["CurrentDataSet"]), Param_Dict["PlotMode"], field))
    saveString += "fig.savefig(plotfilename)  # Takes the name of the file as an argument.\n"
    saveString += 'print("The file has been saved as {0}".format(plotfilename))\n'
    text = plotString + saveString
    if Param_Dict["Timestamp"] and mode in ["Line", "Phase"]:
        text = createCustomTimestampString() + text
    if Param_Dict["LineAnno"] and mode == "Line":
        text = createLinePointAnnoString(Param_Dict) + text
    return text


# %% Functions to construct time series strings
def checkTimeSeriesPlot(Param_Dict, plotAll):
    """Helper function to check whether the user really used the time series
    attribute."""
    # These are the only occurances where the time series is actually used
    if (Param_Dict["XAxis"] == "time" or Param_Dict["TimeSeriesProf"] or
        plotAll):
        return True
    else:
        return False


def constructSeriesString(Param_Dict, plotAll):
    """Constructs the string when handling a time series"""
    loadingString = ("# Load the series through yt and save it as ts:\n"
                     f'ts = yt.load("{Param_Dict["Directory"]}/{Param_Dict["Seriesname"]}")\n\n\n')
    if Param_Dict["XAxis"] == "time":
        plotString = constructProfilePlot(Param_Dict, time=True)
    elif Param_Dict["TimeSeriesProf"]:
        plotString = constructProfilePlot(Param_Dict, multiPlot=True)
    elif plotAll:
        plotString = constructTimeSeriesPlots(Param_Dict)
    text = loadingString + plotString
    return text


def constructTimeSeriesPlots(Param_Dict):
    """Constructs a string to reproduce the loop used to plot pictures of a
    whole series."""
    plotMode = Param_Dict["PlotMode"]
    onlyEvery = Param_Dict["OnlyEvery"]
    loopString = "\n# We are now performing a loop over each file of the dataset:\n"
    loopString += f"directory = '{Param_Dict['Directory']}/{plotMode}plot_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}'\n"
    loopString += "os.mkdir(directory)  # Create a directory to save the frames in\n"
    loopString += f"onlyEvery = {onlyEvery}"
    loopString += "i = 0  # for convenient progress updates\n"
    loopString += "for ds in ts:\n"
    suf = lambda n: "%d%s "%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
    numString = suf(onlyEvery)
    length = len(Param_Dict["DataSeries"])
    loopString += (
f"""    if i % onlyEvery == 0:  # if you only want every {numString} file
        make{plotMode}Plot(ds)
        print(f"Progress: {{(i/{onlyEvery}+1)}}/{math.ceil(length/onlyEvery)} {plotMode}plots done.")
        saveName = f"{{directory}}/{plotMode}plot_{{i+1}}"
        plt.savefig(saveName)
    i += 1
""")
    plotString = "# Here we define the actual plot function that is performed for each frame:\n"
    plotString += f"def make{plotMode}Plot(ds):\n"
    plotString += (
f'''    """A function to produce a {plotMode}plot of the dataset ds using the
    desired parameters.
    Parameters:
        ds: (FLASH)-Dataset loaded using yt
    """
''')
    funcString = eval("construct"+Param_Dict["PlotMode"]+"Plot(Param_Dict)")
    # We need to insert the four spaces because we use this inside of a function
    funcString = funcString.split("\n")
    for line in funcString:
        if line != "":
            plotString += f"    {line}\n"
        else:
            plotString += "\n"
    text = plotString + loopString  # this way the function is defined before it is called
    return text


# %% Functions to construct miscellaneous strings like derived fields, file
# loading and annotations (alphabetical order)
def constructDerFieldString(Param_Dict):
    """Construct a string that reflects the implementation of used custom
    derived fields.
    Returns:
        text: String that is empty in case no custom fields are used
    """
    foundFields = []
    for axis in ["X", "Y", "Z"]:
        fieldName = Param_Dict[axis + "Axis"]
        if (fieldName in Param_Dict["NewDerFieldDict"].keys() and
            fieldName not in foundFields):
            foundFields.append(fieldName)
    text = ""
    for i, fieldName in enumerate(foundFields):
        if i == 0:
            text += "# Adding the custom derived fields that are used:\n"
        displayName = Param_Dict["NewDerFieldDict"][fieldName]["DisplayName"]
        func = Param_Dict["NewDerFieldDict"][fieldName]["FunctionText"]
        unit = Param_Dict["NewDerFieldDict"][fieldName]["Unit"]
        dim = Param_Dict["NewDerFieldDict"][fieldName]["Dimensions"]
        override = Param_Dict["NewDerFieldDict"][fieldName]["Override"]
        if "np." in func:
            text += "import numpy as np\n"
        text += (
f'''# First, define the function that is used for the field:
{func}


# Now we can just add this new field to yt. Another way would be loading the
# dataset(s) first and then add it using ds.add_field(...)
yt.add_field(("gas", "{fieldName}"), function=_{fieldName},
             units="{unit}", dimensions="{dim}", force_override={override},
             display_name=r"{displayName}", take_log=False)


''')
    return text


def createLinePointAnnoString(Param_Dict):
    """Creates a string that can be used to reproduce the lineplot annotation"""
    sNumbers = [Param_Dict[axis + "LStart"] for axis in ["X", "Y", "Z"]]
    eNumbers = [Param_Dict[axis + "LEnd"] for axis in ["X", "Y", "Z"]]
    pointString = (
f'''

# The following functions are used for custom annotation of the start and end
# points used for line plotting
def createLineText(numbers, mode, ds):
    """Creates and returns the text for the line edit.
    Parameters:
        numbers: list of coordinates
        mode: 'Start' or 'End'
        ds: dataset object
    """
    # It is advisable to turn them into a easy-to-read numbers. This is of
    # course optional.
    numbers = yt.YTArray(numbers, "{Param_Dict["LineUnit"]}")
    lengthUnit = ds.get_smallest_appropriate_unit(max(numbers),
                                                  quantity="distance")
    lengths = numbers.to_value(lengthUnit)
    return f"{{mode}}: ({{lengths[0]:.1f}}, {{lengths[1]:.1f}}, {{lengths[2]:.1f}}) {{lengthUnit}}"


def annotateStartEnd(axes, ds):
    """Annotates two boxes for start and end coordinates.
    Parameters:
        axes: mpl axes object for plotting
        ds: yt dataset object for receiving nice units"""
    bboxArgs = {{'boxstyle': 'square,pad=0.3', 'facecolor': 'white',
                'linewidth': 2, 'edgecolor': 'black', 'alpha': 0.5}}
    startText = createLineText({sNumbers}, "Start", ds)
    endText = createLineText({eNumbers}, "End", ds)
    axes.text(x=0.0, y=-0.14, s=startText, size=10, bbox=bboxArgs,
              ha="left", va="bottom", transform=axes.transAxes,
              **{{"color": "black"}})
    axes.text(1.0, -0.14, endText, size=10, bbox=bboxArgs, ha="right",
              va="bottom", transform=axes.transAxes, **{{"color": "black"}})
    print("Annotating line points. Sometimes the positions x and y have "
          "to be adjusted.")
''')
    return pointString


def createCustomTimestampString():
    """Write a string that can be to reproduce the custom timestamp annotation.
    The function call itself has to be added above."""
    stampString = (
'''

# The following two functions are used for a custom timestamp annotation
# because they are not supported for line, phase and profile plots by yt:
def createTimestampText(ds):
    """Creates the text for a timestamp annotation.
    Parameters:
        ds: yt dataset object: To extract the time information from
    """
    timeUnit = ds.get_smallest_appropriate_unit(ds.current_time,
                                                quantity="time")
    time = ds.current_time.to_value(timeUnit)
    return f"t = {time:.1f} {timeUnit}"  # give it a nice look.


def drawTimestampBox(axes, ds):
    """Draw a custom timestamp annotation box like the one
    used by yt on a given axes axes using the dataset ds for information.
    Parameters:
        axes: mpl ax object: The ax to draw the timestamp on
        ds: yt dataset object: To extract the time information from
    """
    bboxArgs = {'boxstyle': 'square,pad=0.3', 'facecolor': 'black',
                'linewidth': 3, 'edgecolor': 'white', 'alpha': 0.5}
    text = createTimestampText(ds)
    axes.text(x=0.03, y=0.96, s=text, size=15, bbox=bboxArgs,
              ha="left", va="top", transform=axes.transAxes, **{"color": "w"})
    # if you leave out the "transform"-keyword, xpos and ypos will be
    # interpreted as data positions.


''')
    return stampString
