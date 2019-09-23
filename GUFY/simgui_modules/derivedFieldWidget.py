# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing all commands used for the creation of the derived field
widget
"""


import numpy as np  # This way the user can use numpy inside of the function definition
import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import yt
from yt.units.unit_registry import UnitParseError
from simgui_modules.checkBoxes import coolCheckBox
from simgui_modules.lineEdits import coolEdit
from simgui_modules.helpWindows import HelpWindow
from simgui_modules.additionalWidgets import GUILogger
from simgui_modules.utils import alertUser
# For the string transformation:
from pygments import highlight
from pygments.lexers import Python3Lexer
from pygments.formatters import HtmlFormatter


def getDerFieldInfo(Param_Dict, ComboBox_Dict, Misc_Dict, dialog):
    """If the user has filled everything in correctly and presses apply, this
    function is called to store the function"""
    # get all of the information from the dialog:
    fieldName = dialog.fieldName
    displayName = dialog.displayName
    fieldFunction = dialog.fieldFunction
    unit = dialog.unit
    dim = dialog.dim
    override = dialog.override
    if dim == 1:
        dim = "dimensionless"
    text = dialog.functionText
    # Add the field to the known fields in Param_Dict and comboboxes:
    for axis in ["X", "Y", "Z"]:
        Param_Dict[axis + "Fields"].insert(3, fieldName)
        ComboBox_Dict[axis + "Axis"].insertItem(3, fieldName)
        if axis != "X":
            ComboBox_Dict[axis + "Weight"].insertItem(3, fieldName)
    Param_Dict["WeightFields"].insert(3, fieldName)
    yt.add_field(("gas", fieldName), function=fieldFunction,
                 units=unit, dimensions=dim, force_override=override,
                 display_name=displayName, take_log=False)
    reloadFiles(Param_Dict, Misc_Dict)
    # Save the parameters in Param_Dict for the ScriptWriting function
    Param_Dict["NewDerFieldDict"][fieldName] = {}
    Param_Dict["NewDerFieldDict"][fieldName]["Override"] = override
    Param_Dict["NewDerFieldDict"][fieldName]["DisplayName"] = displayName
    Param_Dict["NewDerFieldDict"][fieldName]["FunctionText"] = text
    if unit == "auto":
        Param_Dict["NewDerFieldDict"][fieldName]["Unit"] = dialog.baseUnit
    else:
        Param_Dict["NewDerFieldDict"][fieldName]["Unit"] = unit
    Param_Dict["NewDerFieldDict"][fieldName]["Dimensions"] = dim
    if unit == "auto":
        unit = fieldFunction("Hello, I'm a fancy placeholder, why did you \
                             call me?", dialog.sp).units
    ds = Param_Dict["CurrentDataSet"]
    Param_Dict["FieldUnits"][fieldName] = yt.YTQuantity(ds.arr(1, unit)).units
    GUILogger.log(29, f"The new field <b>{fieldName}</b> with {dim}-dimension \
                  has been added successfully.")
    GUILogger.info("You can find it in the comboBoxes for the field selection,"
                   " and it will be added to every new dataset.")


def reloadFiles(Param_Dict, Misc_Dict):
    """After the field has been added, the file or the series have to be
    reloaded."""
    GUILogger.info("Reloading all files so they now about this field.")
    if Param_Dict["isValidSeries"]:
        ts = yt.load(Param_Dict["Directory"] + '/' + Param_Dict["Seriesname"])
        Param_Dict["DataSeries"] = ts
        Misc_Dict["SeriesSlider"].valueChanged.emit(Misc_Dict["SeriesSlider"].value())
    else:
        Param_Dict["SingleDataSet"] = yt.load(Param_Dict["Filename"])
        Param_Dict["CurrentDataSet"] = Param_Dict["SingleDataSet"]


class AskFieldDialog(QW.QDialog):
    """A dialog class for the input of a new derived field for the current
    dataSet. Has built-in-checks for the validity. The user is only able to
    create a new field if everything works properly.
    Parameters:
        fieldList: List of the fields already associated with the dataset
        ds: dataset for the sample point
        parent: QWidget as a parent
    """
    def __init__(self, fieldList, ds, parent):
        super().__init__(parent=parent)
        GUILogger.info("Adding a new derived field. Press the 'Help'-button for more info.")
        self.fieldList = fieldList
        self.fieldName = ""
        self.helpDialog = None
        self.setWindowFlags(QC.Qt.Window |
                            QC.Qt.CustomizeWindowHint |
                            QC.Qt.WindowTitleHint |
                            QC.Qt.WindowMinimizeButtonHint |
                            QC.Qt.WindowMaximizeButtonHint |
                            QC.Qt.WindowCloseButtonHint)
        self.setWindowModality(QC.Qt.WindowModal)  # This way, the user can't interact with main window while this is open
        self.sp = ds.point([0, 0, 0])  # sample data for our tests
        self.initUi()
        self.signalsConnection()
        self.resize(600, 500)
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle("Add new derived field")
        self.show()

    def initUi(self):
        """Initialize all of the elements for the dialog."""
        layout = QW.QGridLayout()
        # Buttons for closing the window:
        self.buttonBox = QW.QDialogButtonBox(self)
        self.buttonBox.addButton("Help", QW.QDialogButtonBox.HelpRole)
        self.buttonBox.addButton("Create Field", QW.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QW.QDialogButtonBox.RejectRole)
        # A line edit for the coming field name, including a validator:
        self.fieldNameEdit = coolEdit(placeholder="e.g. dust_to_gas_density_ratio",
                                      tooltip="Internal name for the new field",
                                      width=None, parent=self)
        nameValidator = QG.QRegExpValidator(QC.QRegExp("[a-zA-Z_]*"))
        self.fieldNameEdit.setValidator(nameValidator)
        # A line edit for the display of the field, coming with a label for display:
        self.displayNameEdit = coolEdit(placeholder="e.g. \\rho_{\\rm d}/\\rh"
                                        "o_{\\rm g}",
                                        tooltip="Raw string input for plotting",
                                        width=None, parent=self)

        # A text edit for the user to enter the function, coming with a label to display errors
        self.fieldFunctionHelperLabel = QW.QLabel("(No python exception)")
        self.fieldFunctionEdit = derivedFieldTextEdit(self.fieldFunctionHelperLabel, parent=self)
        self.unitEdit = coolEdit(placeholder="e.g. msun*m**(-3)*au**3/kg",
                                 tooltip="Set unit for the new field",
                                 width=None)
        self.forceOverrideBox = coolCheckBox(text="Force override (not recommended)",
                                             tooltip="Check this box to overwrite "
                                             "existing fields", width=None)
        layout.addWidget(QW.QLabel("Field name: "), 0, 0)
        layout.addWidget(self.fieldNameEdit, 0, 1, 1, 2)
        layout.addWidget(QW.QLabel("Display name: "), 1, 0)
        layout.addWidget(self.displayNameEdit, 1, 1)
        layout.addWidget(QW.QLabel("Input Function: "), 2, 0)
        layout.addWidget(self.fieldFunctionHelperLabel, 2, 1, 1, 2)
        layout.addWidget(self.fieldFunctionEdit, 3, 0, 1, 3)
        layout.addWidget(QW.QLabel("Unit (can be 'auto'): "), 4, 0)
        layout.addWidget(self.unitEdit, 4, 1, 1, 2)
        layout.addWidget(self.forceOverrideBox, 5, 0, 1, 3)
        layout.addWidget(self.buttonBox, 7, 0, 1, 3)
        self.setLayout(layout)

    def signalsConnection(self):
        """Connects all the signals and emits some of them for a proper start
        """
        self.buttonBox.accepted.connect(self.applyPressed)
        self.buttonBox.rejected.connect(self.cancelPressed)
        self.buttonBox.helpRequested.connect(self.helpPressed)
        self.fieldNameEdit.textChanged.connect(self.validateFieldName)
        self.fieldNameEdit.editingFinished.connect(self.setDisplayName)
        self.unitEdit.textChanged.connect(self.validateUnit)
        self.forceOverrideBox.toggled.connect(self.getOverrideInput)
        self.getOverrideInput(False)
        self.fieldFunctionEdit.editingFinished.connect(self.readFunc)
        self.fieldFunctionEdit.turnBlack()
        self.readFunc()

    def closeEvent(self, event):
        """Reimplement the close event so the helpdialog gets closed as well"""
        super().closeEvent(event)
        if self.helpDialog:
            self.helpDialog.close()
        GUILogger.info("No derived field added.")

    def applyPressed(self):
        self.functionText = self.fieldFunctionEdit.toPlainText()
        displayText = self.displayNameEdit.text()
        if displayText == "":
            self.displayName = self.fieldName
        else:
            self.displayName = displayText
        self.unit = self.unitEdit.text()
        if self.helpDialog:
            self.helpDialog.close()
        self.accept()

    def cancelPressed(self):
        if self.helpDialog:
            self.helpDialog.close()
        self.reject()
        GUILogger.info("No derived field added.")

    def getOverrideInput(self, state):
        """If the user wants to override the current field"""
        self.override = state
        if state:
            alertUser("Forcing an override may cause errors.", "Warning")
        self.validateFieldName(self.fieldNameEdit.text())
        self.setDisplayName()

    def helpPressed(self):
        self.helpDialog = HelpWindow("derived fields", parent=self)
        x = self.geometry().x() + self.width()
        y = self.geometry().y()
        self.helpDialog.move(x, y)
        self.helpDialog.show()

    def readFunc(self):
        """Read the function given through fieldFunctionEdit if possible and
        get the dimensionality of the output"""
        if self.fieldFunctionEdit.isValid:
            text = self.fieldFunctionEdit.toPlainText()
            exec(text, globals())  # this will execute the code once more and save
            self.fieldFunction = eval("_{}".format(self.fieldName))
            try:
                # some of the errors haven't been caught so far, i.e. nameErrors
                unit = self.fieldFunction("Hello, I'm a fancy placeholder, why"
                                          " did you call me?", self.sp).units
                self.baseUnit = unit
                self.dim = unit.dimensions
                self.unitEdit.setPlaceholderText(str(unit))
                if self.unitEdit.text() == "":
                    self.unitEdit.setText(str(unit))
                self.unitEdit.setToolTip("Set the default units to {}-dimension".format(self.dim))
            except Exception as e:
                self.fieldFunctionEdit.turnRed()
                self.fieldFunctionHelperLabel.setText("(Exception: {})".format(e).replace("<string>, ", ""))
                self.fieldFunctionHelperLabel.setStyleSheet("QLabel {color: rgb(255, 0, 0)}")
                self.unitEdit.setPlaceholderText("Please set Field function first.")
        else:
            self.unitEdit.setPlaceholderText("Please set Field function first.")
        self.validateUnit()

    def setDisplayName(self):
        """If no display name has been given, set the display name to fieldName
        """
        if self.displayNameEdit.text() == "":
            self.displayNameEdit.setText(self.fieldNameEdit.text())
            self.displayNameEdit.setPlaceholderText(self.fieldNameEdit.text())
        self.fieldFunctionEdit.validateText()

    def validateApply(self, isValid=True):
        """Enable the apply button if all of the entries by the user are valid,
        else disable it"""
        button = self.buttonBox.buttons()[0]
        if not isValid:
            button.setDisabled(True)
            return
        for wid in [self.fieldNameEdit, self.fieldFunctionEdit, self.unitEdit]:
            if not wid.isValid:
                button.setDisabled(True)
                return
        button.setEnabled(True)

    def validateFieldName(self, text):
        """Checks if the given Name for the derived field is already in the
        list of fields of the dataset."""
        if text in self.fieldList or text == "":
            if self.override and text != "":
                self.fieldNameEdit.turnTextYellow()
                setValidity(self.fieldNameEdit, True)
                self.fieldName = self.fieldNameEdit.text()
            else:
                self.fieldNameEdit.turnTextRed()
                setValidity(self.fieldNameEdit, False)
                self.fieldName = ""
        else:
            self.fieldNameEdit.turnTextBlack()
            setValidity(self.fieldNameEdit, True)
            self.fieldName = self.fieldNameEdit.text()

    def validateUnit(self):
        """Checks whether the unit given matches the dimensionality of the out-
        put of the function."""
        if self.fieldFunctionEdit.isValid:
            if self.unitEdit.text() == "auto":
                self.unitEdit.turnTextBlack()
                setValidity(self.unitEdit, True)
                return
            try:
                unit = yt.YTQuantity(self.sp.ds.arr(1, self.unitEdit.text())).units
                if unit.dimensions == self.dim:
                    self.unitEdit.turnTextBlack()
                    setValidity(self.unitEdit, True)
                else:
                    self.unitEdit.turnTextRed()
                    setValidity(self.unitEdit, False)
            except (UnitParseError, AttributeError):
                self.unitEdit.turnTextRed()
                setValidity(self.unitEdit, False)
        else:
            self.unitEdit.turnTextRed()
            setValidity(self.unitEdit, False)


class derivedFieldTextEdit(QW.QTextEdit):
    """A TextEdit which is used to interpret the text put in for the derived
    fields."""
    editingFinished = QC.pyqtSignal()
    def __init__(self, label, parent=None, *args):
        super().__init__(parent=parent, *args)
        self.infoLabel = label
        self.formatter = HtmlFormatter(nobackground=True, full=True, cssclass="code")
        text = ('''def _(field, data):
    """The function for the new field. See
    https://yt-project.org/doc/developing/creating_derived_fields.html
    for more details.

    numpy as np and yt are already imported and usable.

    You can test the function by pressing CTRL+Return."""
    value = data["pden"] / data["DENSITY"]  # enter possible conversion here
    return value
''')
        text = highlight(text, Python3Lexer(), self.formatter)
        self.setHtml(text)
        self.textCursor().setPosition(36)

    def focusOutEvent(self, event):
        """We want to check our code each time we are finished"""
        self.editingFinished.emit()
        super().focusOutEvent(event)

    def turnRed(self):
        self.setStyleSheet("""QTextEdit {border: 2px solid gray;
                           border-radius: 2px; padding: 1px 1px;
                           border-color: rgb(255,0,0); background-color:
                           rgb(255,228,225)}
                           QTextEdit:focus {border-color: rgb(255,100,100)}
                           QTextEdit:hover {border-color: rgb(255,100,100)}""")
        self.infoLabel.setStyleSheet("QLabel {color: rgb(255, 0, 0)}")
        setValidity(self, False)

    def turnBlack(self):
        self.setStyleSheet("""QTextEdit {border: 2px solid gray;
                           border-radius: 2px; padding: 1px 1px}
                           QTextEdit:focus {border-color: rgb(79,148,205)}
                           QTextEdit:hover {border-color: rgb(79,148,205)}""")
        self.infoLabel.setStyleSheet("QLabel {color: rgb(0, 0, 0)}")
        setValidity(self, True)

    def keyPressEvent(self, event):
        """We need to reimplement this event to grab the enter key and to
        validate our text"""
        if event.modifiers() ==  QC.Qt.ControlModifier and event.key() == QC.Qt.Key_Return:
            self.editingFinished.emit()  # This way, the user can run the function by pressing Ctrl+Enter
            return
        text = self.toPlainText()
        if event.key() == 16777217 and event.modifiers() == QC.Qt.NoModifier:  # this corresponds to tab
            self.insertPlainText(" "*4)
        else:
            super().keyPressEvent(event)
        if event.modifiers() ==  QC.Qt.ControlModifier:  # this corresponds to crtl/strg
            pass
        else:
            splitText = self.toPlainText().split("\n")
            if event.key() == QC.Qt.Key_Shift:
                return
            if not splitText[-1].startswith("    return"):
                self.restoreText(text)
                return
            if event.key() == 16777220:  # this corresponds to enter
                self.insertPlainText(" "*4)
                return
            self.validateText()  # this will unfortunately deselect any text.

    def validateText(self):
        """Function that validates the text in a way we need it to be"""
        text = self.toPlainText()
        splitText = text.split("\n")
        if splitText[0] != "def _{}(field, data):".format(self.parent().fieldName):
            splitText[0] = "def _{}(field, data):".format(self.parent().fieldName)
            text = "\n".join(splitText)
        else:
            self.turnBlack()
        try:
            # this will try to execute the function
            exec(text)
            self.infoLabel.setText("(No python exception)")
            self.turnBlack()
        except Exception as e:
            self.turnRed()
            self.infoLabel.setText(f"(Exception: {e})".replace("<string>, ", ""))
        self.restoreText(text)

    def restoreText(self, text):
        """Takes the text and displays it in python style syntax. Unfortunately
        this is a pretty clunky way of doing it, but it wouldn't work otherwise
        """
        pos = self.textCursor().position()
        text = highlight(text, Python3Lexer(), self.formatter)
        textSplit = text.split("</pre>")
        textSplit[0] = textSplit[0].strip()
        text = "</pre>".join(textSplit)
        self.setHtml(text)
        for i in range(pos):
            self.moveCursor(QG.QTextCursor.NextCharacter)


def setValidity(wid, isValid):
    """Sets the validity of the given widget wid and calls its parentmethod."""
    if isValid:
        wid.isValid = True
        wid.parent().validateApply()
    else:
        wid.isValid=False
        wid.parent().validateApply(False)
    return
