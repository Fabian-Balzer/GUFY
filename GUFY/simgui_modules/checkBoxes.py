# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the CheckBoxes
"""


import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW


class coolCheckBox(QW.QCheckBox):
    """Modified version of QCheckBoxes.
    Creates a QCheckBox with a given text and tooltip.
    params:
        text: Text to be shown
        tooltip: optionally create a tooltip for the edit
        checked: Bool set to false by default.
    """
    def __init__(self, text=None, tooltip=None, checked=False, width=150):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        self.setChecked(checked)
        if width is not None:
            self.setFixedWidth(width)
        self.setStyleSheet("""QCheckBox {color: rgb(0, 0, 0); height: 18 px}
QCheckBox::indicator:unchecked {
    image: url(simgui_registry/Icons/CheckBoxUncheckedBase.png); height: 17 px}
QCheckBox::indicator:unchecked:hover {
    image: url(simgui_registry/Icons/CheckBoxUncheckedHover.png); height: 17 px;}
QCheckBox::indicator:unchecked:pressed {
    image: url(simgui_registry/Icons/CheckBoxUncheckedPressed.png); height: 17 px;}
QCheckBox::indicator:unchecked:disabled {
    image: url(simgui_registry/Icons/CheckBoxUncheckedDisabled.png); height: 17 px;}
QCheckBox::indicator:checked {
    image: url(simgui_registry/Icons/CheckBoxCheckedBase.png); height: 17 px;}
QCheckBox::indicator:checked:hover {
    image: url(simgui_registry/Icons/CheckBoxCheckedHover.png); height: 17 px}
QCheckBox::indicator:checked:pressed {
    image: url(simgui_registry/Icons/CheckBoxCheckedPressed.png); height: 17 px}
QCheckBox::indicator:checked:disabled {
    image: url(simgui_registry/Icons/CheckBoxCheckedDisabled.png); height: 17 px}""")


# %% Creation
def createAllCheckBoxes(Param_Dict, CheckBox_Dict):
    """Creates all necessary CheckBoxes and stores them in CheckBox_Dict
    params:
        Param_Dict: For storing output
        CheckBox_Dict: Dict to contain all the checkBoxes
    """
    hand = Param_Dict["SignalHandler"]
    AnnotationBoxes = createAnnotationBoxes()
    LogBoxes = createLogBoxes()
    ProfileBoxes = createProfileBoxes()
    Boxes = AnnotationBoxes + LogBoxes + ProfileBoxes  # Merge the lists
    keys = ["Timestamp", "Scale", "Grid", "VelVectors", "VelStreamlines",
            "MagVectors", "MagStreamlines", "Contour", "ParticleAnno",
            "LineAnno", "XLog",
            "YLog", "ZLog", "AddProfile", "TimeSeriesProf"]
    for i, key in enumerate(keys):
        CheckBox_Dict[key] = Boxes[i]
    CheckBox_Dict["DomainDiv"] = createDomainDivBox()
    CheckBox_Dict["SetAspect"] = coolCheckBox("Ignore aspect ratio",
                                              "If checked, the plot may not "
                                              "have the default aspect.",
                                              width=None)
    CheckBox_Dict["CommentsForPlot"] = coolCheckBox("Enable script comments",
                                                    "If checked, the output sc"
                                                    "ript will have comments "
                                                    "with suggestions in it",
                                                    True, width=200)
    CheckBox_Dict["ParticlePlot"] = createParticlePlotBox()
    CheckBox_Dict["ParticlePlot"].toggled.connect(lambda: hand.getParticleInput())
    CheckBox_Dict["Timestamp"].toggled.connect(lambda: hand.getAnnotationInput("Timestamp"))
    CheckBox_Dict["Scale"].toggled.connect(lambda: hand.getAnnotationInput("Scale"))
    CheckBox_Dict["Grid"].toggled.connect(lambda: hand.getAnnotationInput("Grid"))
    CheckBox_Dict["VelVectors"].toggled.connect(lambda: hand.getAnnotationInput("VelVectors"))
    CheckBox_Dict["VelStreamlines"].toggled.connect(lambda: hand.getAnnotationInput("VelStreamlines"))
    CheckBox_Dict["MagVectors"].toggled.connect(lambda: hand.getAnnotationInput("MagVectors"))
    CheckBox_Dict["MagStreamlines"].toggled.connect(lambda: hand.getAnnotationInput("MagStreamlines"))
    CheckBox_Dict["Contour"].toggled.connect(lambda: hand.getAnnotationInput("Contour"))
    CheckBox_Dict["ParticleAnno"].toggled.connect(lambda: hand.getAnnotationInput("ParticleAnno"))
    CheckBox_Dict["LineAnno"].toggled.connect(lambda: hand.getAnnotationInput("LineAnno"))
    CheckBox_Dict["XLog"].toggled.connect(lambda: hand.getAnnotationInput("XLog"))
    CheckBox_Dict["YLog"].toggled.connect(lambda: hand.getAnnotationInput("YLog"))
    CheckBox_Dict["ZLog"].toggled.connect(lambda: hand.getAnnotationInput("ZLog"))
    CheckBox_Dict["AddProfile"].toggled.connect(lambda: hand.getAddProfileInput())
    CheckBox_Dict["TimeSeriesProf"].toggled.connect(lambda: hand.getAnnotationInput("TimeSeriesProf"))
    CheckBox_Dict["DomainDiv"].toggled.connect(lambda: hand.getDomainDivInput())
    CheckBox_Dict["SetAspect"].toggled.connect(lambda: hand.getAnnotationInput("SetAspect"))
    CheckBox_Dict["CommentsForPlot"].toggled.connect(lambda: hand.getAnnotationInput("CommentsForPlot"))
    return


def createAnnotationBoxes(width=200, defaultString=" "):
    """Creates CheckBoxes where the user can toggle annotations for the plot.
    returns:
        boxList: List containing the checkboxes
    """
    texts = ["Timestamp", "Scale", "Grid", "Velocity vectors",
             "Velocity Streamlines",
             "Magnetic field vectors", "Magnetic field Streamlines",
             "Contour lines", "Particles", "Start and end point"]
    tooltips = [f"Toggle {defaultString}{text.lower()} annotation" for text in texts]
    boxList = []
    for i, text in enumerate(texts):
        CB = coolCheckBox(text, tooltips[i], width=width)
        boxList.append(CB)
    boxList[-1].setFixedWidth(100)
    boxList[0].setChecked(True)
    return boxList


def createLogBoxes():
    """Creates CheckBoxes where the user can select logarithmic scaling of an
    axis.
    returns:
        boxList: List containing the checkboxes
    """
    texts = ["Horizontal axis", "Vertical axis", "Color axis"]
    tooltips = ["Set " + axis + " logarithmic" for axis in texts]
    boxList = []
    for text, tooltip in zip(texts, tooltips):
        CB = coolCheckBox(text, tooltip)
        boxList.append(CB)
    boxList[1].setChecked(True)
    boxList[2].setChecked(True)
    return boxList


def createProfileBoxes():
    """Create two CheckBoxes that are used to make multiple plots for either
    multiple fields or multiple times possible.
    """
    texts = ["Add a second Profile", ""]
    tooltips = ["If checked, the selected field will be added to the current "
                "plot instead of overwriting it", "Plot the field for multiple"
                " times"]
    boxList = []  # "AddProfile", "TimeSeriesProf" are the names they are saved as
    for text, tooltip in zip(texts, tooltips):
        CB = coolCheckBox(text, tooltip)
        boxList.append(CB)
    boxList[1].setFixedWidth(20)
    boxList[0].setDisabled(True)  # This will only be enabled if the plotWindow aready has a profile plot
    boxList[1].setHidden(True)  # This will only be shown in time series mode
    return boxList


def createDomainDivBox():
    """Creates a CheckBox that can be checked so during projection, the result
    of projection is divided by the domain height"""
    domainDivBox = coolCheckBox("Divide by height", "Divide the result of "
                                "projection by the domain height")
    return domainDivBox


def createParticlePlotBox():
    """Creates a CheckBox that can be checked during phase or projection to
    plot particle instead of gas fields."""
    pbox = coolCheckBox("Particle plot", "Changes the fields to "
                        "the available particle fields of the dataset.",
                        width=None)
    return pbox
