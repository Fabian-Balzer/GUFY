# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the labels
"""


import PyQt5.QtWidgets as QW


class coolLabel(QW.QLabel):
    """Modified version of QLabels.
    Creates a QLabel with a given text and tooltip.
    params:
        text: Text to be shown
        tooltip: optionally create a tooltip for the label
    """
    def __init__(self, text="", tooltip="", width=False, style=True):
        super().__init__()
        self.setText(text)
        self.setToolTip(tooltip)
        if width:
            self.setMinimumWidth(50)
            self.setMaximumWidth(100)
        if style:
            self.setStyleSheet("""QLabel {border: 0px solid gray;
                               border-radius: 0px; padding: 1px 1px;
                               color: rgb(0,0,0); height: 18px}""")


def createAllLabels(Label_Dict):
    """Creates all necessary Labels and stores them in Label_Dict
    params:
        Label_Dict: Dict to contain all the QLabels
    """
    labelKeys = ["XMinUnit", "YMinUnit", "ZMinUnit", "XMaxUnit", "YMaxUnit",
                 "ZMaxUnit",
                 "XCenUnit", "YCenUnit", "ZCenUnit", "HorWidthUnit",
                 "VerWidthUnit"]
    for key in labelKeys:
        Label_Dict[key] = coolLabel("", width=True)
    labelKeys = ["CurrentDataSet", "DataSetTime", "Geometry", "Dimensions"]
    for key in labelKeys:
        Label_Dict[key] = coolLabel("", width=False)
    Label_Dict["LineLength"] = coolLabel("", "Displays the length of the line",
                                         style=False)
    for axis in ["X", "Y", "Z"]:
        Label_Dict[axis + "Center"] = coolLabel(text=f"Center {axis.lower()}:",
                                                width=False, style=False)
