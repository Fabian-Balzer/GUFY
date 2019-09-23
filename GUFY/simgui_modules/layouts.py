# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Contains functions and methods concerning the layout of the simulation_gui.
Sorted in alphabetical order.
"""


import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW


def createAllWidgets(Window):
    """Creates BoxLayouts and stores them in Wid_Dict"""
    # I know this is ugly, but this way only Window needed to be passed.
    (Wid_Dict, ComboBox_Dict, RadioDict_Dict, Edit_Dict, Button_Dict,
     CheckBox_Dict, Label_Dict, Param_Dict, Misc_Dict) = (Window.Wid_Dict,
        Window.ComboBox_Dict, Window.RadioDict_Dict,
        Window.Edit_Dict, Window.Button_Dict, Window.CheckBox_Dict,
        Window.Label_Dict, Window.Param_Dict, Window.Misc_Dict)
    # Create the radio button layouts
    Wid_Dict["EvalMode"] = RBWidget(RadioDict_Dict["EvalMode"], "Evaluation mode")
    Wid_Dict["1DOptions"] = RBWidget(RadioDict_Dict["1DOptions"], "1D plot options", Button_Dict)
    Wid_Dict["2DOptions"] = RBWidget(RadioDict_Dict["2DOptions"], "2D plot options", Button_Dict)
    Wid_Dict["DimMode"] = RBWidget(RadioDict_Dict["DimMode"], "Plot dimension")
    Wid_Dict["NormVecMode"] = RBWidget(RadioDict_Dict["NormVecMode"], "Normal vector")
    Wid_Dict["DataSeriesLabels"] = createHorLayout([QW.QLabel("Selected Dataset: "),
                                                   Label_Dict["CurrentDataSet"],
                                                   Label_Dict["DataSetTime"],
                                                   Label_Dict["Dimensions"],
                                                   Label_Dict["Geometry"]])
    Wid_Dict["NormInput"] = createHorLayout([Edit_Dict["XNormDir"],
                                            Edit_Dict["YNormDir"],
                                            Edit_Dict["ZNormDir"]],
                                            spacing=3)
    Wid_Dict["NorthInput"] = createHorLayout([Edit_Dict["XNormNorth"],
                                             Edit_Dict["YNormNorth"],
                                             Edit_Dict["ZNormNorth"]],
                                             spacing=3)
    # Create the puzzle pieces the layout is made of:
    Wid_Dict["FileOptions"] = fileOptions(Wid_Dict["EvalMode"], Button_Dict,
                                          Param_Dict, Misc_Dict, Wid_Dict)
    Wid_Dict["XAxis"] = axisOptions("X", ComboBox_Dict, Edit_Dict,
                                    CheckBox_Dict, Button_Dict,
                                    Label_Dict, ComboBox_Dict)
    Wid_Dict["YAxis"] = axisOptions("Y", ComboBox_Dict, Edit_Dict,
                                    CheckBox_Dict, Button_Dict,
                                    Label_Dict, ComboBox_Dict)
    Wid_Dict["ZAxis"] = axisOptions("Z", ComboBox_Dict, Edit_Dict,
                                    CheckBox_Dict, Button_Dict,
                                    Label_Dict, ComboBox_Dict)
    Wid_Dict["NAxis"] = normalAxisOptions(Wid_Dict, ComboBox_Dict, Edit_Dict,
                                          Label_Dict)
    Wid_Dict["LineOptions"] = lineOptions(Edit_Dict, Label_Dict)
    Wid_Dict["SlcProjOptions"] = slcProjOptions(Edit_Dict, Button_Dict,
                                                Label_Dict, CheckBox_Dict)
    Wid_Dict["ProfileOptions"] = profileOptions(CheckBox_Dict, ComboBox_Dict,
                                                Misc_Dict)
    Wid_Dict["AnnotationOptions"] = annotationOptions(CheckBox_Dict, Edit_Dict)
    Wid_Dict["ParticlePlot"] = particleOptions(CheckBox_Dict)
    Wid_Dict["PlotOptions"] = plotOptions(Wid_Dict, Button_Dict)
    Wid_Dict["TopLayout"] = createMainLayout(Wid_Dict, Window._main)


def createMainLayout(Wid_Dict, _main):
    """Makes the main layout for the GUI by placing the file and plot options
    and leaving a space for the PlotWindow to be added later.
    Return:
        topLayout: top layout of the GUI. The mainLayout isn't needed later."""
    # One big layout to contain overall structure
    mainLayout = QW.QGridLayout(_main)
    mainLayout.setContentsMargins(1, 1, 1, 1)
    # A top one to contain plotting and plot mode
    mainWidget = QW.QWidget()
    mainLayout.addWidget(mainWidget, 0, 0)
    topLayout = QW.QGridLayout(mainWidget)
    topLayout.addWidget(Wid_Dict["FileOptions"], 0, 1)  # top right for FileOptions
    topLayout.setContentsMargins(1, 1, 1, 1)
    topLayout.setColumnStretch(0, 1)
    for row in range(2):
        mainLayout.setRowStretch(row, 1+row)
    mainLayout.addWidget(Wid_Dict["PlotOptions"], 1, 0)
    return topLayout  # Store it in Wid_Dict for later use


def annotationOptions(CheckBox_Dict, Edit_Dict):
    """Creates the GroupBox for the annotation options
    params:
        CheckBox_Dict: Dictionary witht the necessary CheckBoxes in it
    returns:
        wid: QGroupBox in FormLayout
    """
    wid = QW.QGroupBox("Annotation options")
    box = QW.QVBoxLayout(wid)
    scroll = QW.QScrollArea(wid)
    box.addWidget(scroll)
    scroll.setWidgetResizable(True)
    scrollContent = QW.QGroupBox(scroll)
    scrollLayout = QW.QVBoxLayout()
    scrollLayout.setContentsMargins(0, 0, 0, 0)
    scrollContent.setLayout(scrollLayout)
    scrollLayout.setSpacing(3)
    keys = ["Timestamp", "Scale", "Grid", "Contour",
            "VelVectors", "VelStreamlines",
            "MagVectors", "MagStreamlines", "LineAnno"]
    scrollLayout.addWidget(Edit_Dict["PlotTitle"])
    for key in sorted(keys):
        scrollLayout.addWidget(CheckBox_Dict[key])
    scrollLayout.insertWidget(6, createHorLayout([CheckBox_Dict["ParticleAnno"],
                              Edit_Dict["PSlabWidth"]]))
    scrollLayout.addStretch(1)
    scroll.setWidget(scrollContent)
    scrollContent.setStyleSheet("QGroupBox {border: transparent}")
    return wid


def axisOptions(axis, Box_Dict, Edit_Dict, CheckBox_Dict, Button_Dict,
                Label_Dict, ComboBox_Dict):
    """Creates the AxisOptions Layout and returns it as a widget.
    params:
        axis: "X", "Y", "Z"
        Box_Dict: Dictionary for ComboBoxes
        Edit_Dict: Dictionary for LineEdits
        Button_Dict: For the buttons to calculate min/max
    returns:
        wid: GroupBox in FormLayout that hosts the relevant stuff.
    """
    if axis == "X":
        text = "Horizontal"
    elif axis == "Y":
        text = "Vertical"
    elif axis == "Z":
        text = "Colorbar"
    wid = QW.QGroupBox(text)
    layout = QW.QFormLayout(wid)
    layout.setVerticalSpacing(3)
    layout.addRow(QW.QLabel("Field:"), Box_Dict[axis + "Axis"])
    if axis == "Y":
        layout.addRow(QW.QLabel("Quantity:"), ComboBox_Dict["TimeQuantity"])
    layout.addRow(QW.QLabel("Min:"), createHorLayout([Edit_Dict[axis +"Min"], Label_Dict[axis + "MinUnit"]]))
    layout.addRow(QW.QLabel("Max:"), createHorLayout([Edit_Dict[axis +"Max"], Label_Dict[axis + "MaxUnit"]]))
    layout.addRow(QW.QLabel("Unit:"), Edit_Dict[axis +"Unit"])
    layout.addRow(QW.QLabel("Log Scaling:"), CheckBox_Dict[axis +"Log"])
    if axis == "Z":
        layout.addRow(QW.QLabel("Weight field:"), ComboBox_Dict["ZWeight"])
        layout.addRow(QW.QLabel("Colors:"), Edit_Dict["ColorScheme"])
        layout.addRow(QW.QLabel("Norm:"), CheckBox_Dict["DomainDiv"])
    layout.addWidget(createHorLayout([Button_Dict[axis + "Calc"], Button_Dict[axis + "Recalc"]]))
    return wid


def createHorLayout(widList, stretch=True, spacing=0):
    """Create horizontal box layout widget containing widgets in widList"""
    wid = QW.QWidget()
    wid.setStyleSheet("""QWidget {border: 0px solid gray;
                           border-radius: 0px; padding: 0, 0, 0, 0}""")
    layout = QW.QHBoxLayout(wid)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for widget in widList:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch(1)
    return wid


def fileOptions(EvalMode, Button_Dict, Param_Dict, Misc_Dict,
                Wid_Dict):
    """Creates the FileOptionsLayout and returns it as a widget.
    params:
        EvalMode: Radio Buttons
        Button_Dict: Dictionary for Buttons
    returns:
        wid: GroupBox in VBoxLayout that hosts the relevant stuff.
    """
    wid = QW.QGroupBox("File options")
    layout = QW.QVBoxLayout(wid)
    layout.setSpacing(20)
    layout.addWidget(EvalMode)
    layout.addWidget(Button_Dict["Open"])
    if Param_Dict["TestingMode"]:
        layout.addWidget(Button_Dict["QuickCart"])
#        layout.addWidget(Button_Dict["QuickCyli"])
        layout.addWidget(Button_Dict["QuickSeries"])
    layout.addWidget(createHorLayout([Button_Dict["Evaluate"], Button_Dict["PlotAll"]], stretch=False))
    if Param_Dict["TestingMode"]:
        layout.addWidget(Button_Dict["PrintDict"])
    layout.addWidget(Wid_Dict["DataSeriesLabels"])
    layout.addWidget(Misc_Dict["SeriesSlider"])
    layout.addWidget(Misc_Dict["LogBox"])
    layout.setContentsMargins(3, 3, 3, 3)
    wid.setFixedWidth(500)
    return wid


def hideShowLabels(FormLayout, start, end, hide=True):
    """Hides and shows widgets in a form Layout at the given positions.
    params:
        FormLayout: The layout to perform hide/show on
        start, end: starting and ending point of hiding/showing
        hide: bool. True for hiding, False for showing."""
    for i in range(start, end+1):
        FormLayout.layout().itemAt(i).widget().setHidden(hide)


def lineOptions(Edit_Dict, Label_Dict):
    """Creates the lineOptions for linePlotting and returns them as a widget.
    params:
        Edit_Dict: We need to place start and end points and unit lineEdit
    returns:
        wid: GroupBox
    """
    wid = QW.QGroupBox("Line plot options")
    pointLayout = QW.QVBoxLayout(wid)
    pointLayout.setSpacing(3)
    pointLayout.addWidget(QW.QLabel("Start point (X, Y, Z):"))
    startLayout = createHorLayout([Edit_Dict["XLStart"], Edit_Dict["YLStart"],
                                   Edit_Dict["ZLStart"]], spacing=3)
    pointLayout.addWidget(startLayout)
    pointLayout.addWidget(QW.QLabel("End point (X, Y, Z):"))
    endLayout = createHorLayout([Edit_Dict["XLEnd"], Edit_Dict["YLEnd"],
                                 Edit_Dict["ZLEnd"]], spacing=3)
    pointLayout.addWidget(endLayout)
    unitLayout = createHorLayout([QW.QLabel("Unit:"), Edit_Dict["LineUnit"]],
                                 spacing=10)
    pointLayout.addWidget(unitLayout)
    pointLayout.addWidget(Label_Dict["LineLength"])
    pointLayout.addStretch(1)
    return wid


def normalAxisOptions(Wid_Dict, ComboBox_Dict, Edit_Dict, Label_Dict):
    """Creates the AxisOptions Layout and returns it as a widget.
    params:
        Wid_Dict: For the prefactured widgets
        ComboBox_Dict: Dictionary for ComboBoxes
    returns:
        wid: GroupBox
    """
    wid = QW.QGroupBox("Normal vector options")
    layout = QW.QVBoxLayout(wid)
    layout.setSpacing(3)
    layout.addWidget(Wid_Dict["NormVecMode"])
    layout.addWidget(createHorLayout([QW.QLabel("Normal Axis:"), ComboBox_Dict["NAxis"]], spacing=5))
    layout.addWidget(QW.QLabel("Off-axis normal vector direction:"))
    layout.addWidget(Wid_Dict["NormInput"])
    layout.addWidget(QW.QLabel("North vector direction:"))
    layout.addWidget(Wid_Dict["NorthInput"])
    layout.addStretch(1)
    return wid


def plotOptions(Wid_Dict, Button_Dict):
    """Creates the First Layout for the options.
    params:
        Wid_Dict: Dictionary containing the widgets to add
    returns:
        wid: QGridLayout with widgets
    """
    wid = QW.QGroupBox("Plot options")
    layout = QW.QGridLayout(wid)
    layout.addWidget(Wid_Dict["DimMode"], 0, 0)
    layout.addWidget(Wid_Dict["1DOptions"], 0, 1)
    layout.addWidget(Wid_Dict["2DOptions"], 0, 1)
    layout.addWidget(Wid_Dict["ParticlePlot"], 0, 2)
    layout.addWidget(createHorLayout([Button_Dict["WriteScript"], Button_Dict["AddDerField"]], False), 0, 3)
    layout.addWidget(Wid_Dict["XAxis"], 1, 0)
    layout.addWidget(Wid_Dict["NAxis"], 1, 0)
    layout.addWidget(Wid_Dict["YAxis"], 1, 1)
    layout.addWidget(Wid_Dict["SlcProjOptions"], 1, 1)
    layout.addWidget(Wid_Dict["ZAxis"], 1, 2)
    layout.addWidget(Wid_Dict["ProfileOptions"], 1, 2)
    layout.addWidget(Wid_Dict["LineOptions"], 1, 0)
    layout.addWidget(Wid_Dict["AnnotationOptions"], 1, 3)
    layout.setContentsMargins(3, 0, 3, 3)
    for column in range(4):
        layout.setColumnStretch(column, 1)
        layout.setColumnMinimumWidth(column, 300)
    scroll = QW.QScrollArea()
    scroll.setWidget(wid)
    scroll.setWidgetResizable(True)
    scroll.setMinimumHeight(200)
    scroll.setMaximumHeight(380)
    scroll.setStyleSheet("QScrollArea {border: transparent}")
    return scroll


def profileOptions(CheckBox_Dict, ComboBox_Dict, Misc_Dict):
    """Creates the layout that is displayed for profile plots.
    Params:
        CheckBox_Dict: For adding time series checkboxes
        ComboBox_Dict: For adding weight fields
        Misc_Dict: For adding spin box
    Returns:
        wid: QGridLayout"""
    wid = QW.QGroupBox("Profile plot options")
    layout = QW.QGridLayout(wid)
    layout.setVerticalSpacing(3)
    layout.addWidget(QW.QLabel("Weight Field:"), 1, 0)
    layout.addWidget(ComboBox_Dict["YWeight"], 1, 1)
    layout.addWidget(CheckBox_Dict["AddProfile"], 2, 0, 1, 2)
    layout.addWidget(createHorLayout([CheckBox_Dict["TimeSeriesProf"],
                                     Misc_Dict["ProfileSpinner"]]), 3, 0, 1, 2)
    layout.setRowStretch(4, 1)
    return wid


def RBWidget(Dict, text=None, Button_Dict=None):
    """Takes a dict of radio buttons and group them in their own horizontal
    Box layout.
    params:
        Dict: Dictionary containing radio buttons
        text: In case the group is supposed to have an outline and heading
        Button_Dict: In case the help button should be added
    returns:
        wid: widget in QHBoxLayout"""
    if text is None:
        wid = QW.QWidget()
    else:
        wid = QW.QGroupBox(text)
    layout = QW.QHBoxLayout(wid)
    layout.setContentsMargins(5, 0, 5, 5)
    for button in Dict.values():
        layout.addWidget(button)
    layout.addStretch(1)
    if "1D" in text:
        layout.addWidget(Button_Dict["PlotHelp1D"])
    if "2D" in text:
        layout.addWidget(Button_Dict["PlotHelp2D"])
    wid.setFixedHeight(50)
    return wid


def particleOptions(CheckBox_Dict):
    """Create a group box holding the 'toggle particles' widget"""
    wid = QW.QGroupBox("Particle options")
    layout = QW.QGridLayout(wid)
    layout.addWidget(CheckBox_Dict["ParticlePlot"])
    layout.setContentsMargins(11, 0, 1, 0)
    return wid


def slcProjOptions(Edit_Dict, Button_Dict, Label_Dict, CheckBox_Dict):
    """Constructs the additional options needed for slice/projection plotting.
    params:
        Edit_Dict, Button_Dict: Widgets added
    returns:
        wid: QGroupBox with widgets
    """
    wid = QW.QGroupBox("Slice plot options")
    layout = QW.QFormLayout(wid)
    layout.setSpacing(3)
    layout.addRow(QW.QLabel("Grid Unit:"), Edit_Dict["GridUnit"])
    layout.addRow(Label_Dict["XCenter"], createHorLayout([Edit_Dict["XCenter"], Label_Dict["XCenUnit"]]))
    layout.addRow(Label_Dict["YCenter"], createHorLayout([Edit_Dict["YCenter"], Label_Dict["YCenUnit"]]))
    layout.addRow(Label_Dict["ZCenter"], createHorLayout([Edit_Dict["ZCenter"], Label_Dict["ZCenUnit"]]))
    layout.addRow(QW.QLabel("Hor. width: "), createHorLayout([Edit_Dict["HorWidth"], Label_Dict["HorWidthUnit"]]))
    layout.addRow(QW.QLabel("Vert. width: "), createHorLayout([Edit_Dict["VerWidth"], Label_Dict["VerWidthUnit"]]))
    layout.addRow(QW.QLabel("Zoom:"), Edit_Dict["Zoom"])
    layout.addWidget(Button_Dict["MakeLinePlot"])
    layout.addWidget(CheckBox_Dict["SetAspect"])
    return wid
