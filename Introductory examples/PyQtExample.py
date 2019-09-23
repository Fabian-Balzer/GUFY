# -*- coding: utf-8 -*-
"""
PyQt_Example
Created on Sat Jul 20 12:39:00 2019

@author: Fabian Balzer
"""
import sys
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC
import PyQt5.QtWidgets as QW  # This is the main module used


class ApplicationWindow(QW.QMainWindow):  # Inherit from QMainWindow
    def __init__(self):  # This is called whenever an instance is created
        super().__init__()  # Initialize it as usual
        self.setWindowIcon(QG.QIcon('../../simgui_registry/yt_gui_icon.png'))
        self.setWindowTitle("PyQt example window")
        self.setGeometry(100, 100, 600, 400)
        self._main = QW.QWidget()  # Create a widget to hold the layout
        self.setCentralWidget(self._main)  # Add it to ApplicationWindow
        mainLayout = QW.QFormLayout(self._main)  # Create layout on it
        self.exampleCheckBox = QW.QCheckBox("This can be either ticked or not")
        self.exampleComboBox = createQComboBox()
        self.exampleLabel = QW.QLabel("Labels can contain text or pictures")
        self.exampleLineEdit = createQLineEdit()
        self.examplePushButton = QW.QPushButton("This can be pressed for an output")
        self.exampleRadioGroup = createQRadioButtons()
        self.exampleSlider = createQSlider()
        self.exampleSpinBox = createQSpinBox()
        self.exampleStatusBar = createQStatusBar()
        self.exampleTextBrowser = createQTextBrowser()
        mainLayout.addRow("QCheckBox: ", self.exampleCheckBox)  # Add CheckBox to layout
        mainLayout.addRow("QComboBox: ", self.exampleComboBox)  # Add ComboBox to layout
        mainLayout.addRow("QLabel: ", self.exampleLabel)  # Add label to layout
        mainLayout.addRow("QLineEdit: ", self.exampleLineEdit)  # Add LineEdit to layout
        mainLayout.addRow("QPushButton: ", self.examplePushButton)  # Add PushButton to layout
        mainLayout.addRow("QRadioButton: ", self.exampleRadioGroup)  # Add RadioButtons to layout
        mainLayout.addRow("QSlider: ", self.exampleSlider)  # Add Slider to layout
        mainLayout.addRow("QSpinBox: ", self.exampleSpinBox)  # Add SpinBox to layout
        mainLayout.addRow("QTextBrowser/TextEdit: ", self.exampleTextBrowser)  # Add TextBrowser to layout
        self.setStatusBar(self.exampleStatusBar)  # Add a StatusBar to the window
        # For taking a sceenshot
        self.preview_screen = QW.QApplication.primaryScreen().grabWindow(0)


def createQComboBox():
    """Creates and returns a QComboBox filled with items for the example"""
    comboBox = QW.QComboBox()
    comboBox.addItems(["Select one of the options given",
                       "You can add whatever text you want",
                       "You could even insert icons"])
    return comboBox


def createQLineEdit():
    """Creates and returns a QLineEdit with a placeholder for the example"""
    lineEdit = QW.QLineEdit()
    lineEdit.setPlaceholderText("This is a placeholder. LineEdits can have "
                                "validators for the text as well.")
    return lineEdit


def createQRadioButtons():
    """Creates a group of radio buttons and returns them in a group box for the
    example"""
    groupBox = QW.QGroupBox("QRadioButtons in a QGroupBox")
    layout = QW.QHBoxLayout()
    for name in ["Only one", "Button of a group", "can be checked at once"]:
        RadioButton = QW.QRadioButton(name)
        layout.addWidget(RadioButton)
    RadioButton.setChecked(True)  # Check the last radio button
    groupBox.setLayout(layout)
    # Multiple RadioButton groups can be made using QW.QButtonGroup(MainWidget)
    # and then adding the buttons to the desired groups
    return groupBox


def createQSlider():
    """Creates and returns a QSlider for the example"""
    slider = QW.QSlider(QC.Qt.Horizontal)
    slider.setRange(0, 20)
    slider.setTickPosition(QW.QSlider.TicksBelow)
    slider.setTickInterval(1)
    slider.setValue(8)
    return slider


def createQSpinBox():
    """Creates and returns a QSpinBox for the example"""
    spinBox = QW.QSpinBox()
    spinBox.setRange(20, 50)
    spinBox.setValue(42)
    spinBox.setPrefix("SpinBoxes can have a prefix before... ")
    spinBox.setSuffix(" ...and a suffix after the number")
    return spinBox


def createQStatusBar():
    """Creates and returns a statur bar for the example"""
    bar = QW.QStatusBar()
    statusLabel1 = QW.QLabel("QStatusBar: ")
    bar.addPermanentWidget(statusLabel1, 1)
    statusLabel2 = QW.QLabel("A statusbar usually briefly displays important "
                            "and relevant information.")
    bar.addPermanentWidget(statusLabel2, 1)
    return bar


def createQTextBrowser():
    """Creates and return a QTextBrowser for the example"""
    browser = QW.QTextBrowser()
    text = (
            '''<p>The text of <b>QTextBrowsers</b> or their editable version,
            <b>QTextEdits</b>, can be set using HTML.</p>
            <p>Click on <a href="https://doc.qt.io/qt-5/qtextbrowser.html">
            this link</a> for more information on QTextBrowsers, or
            on <a href="https://doc.qt.io/qt-5/gallery.html">this link</a> to
            get more information about QWidgets in general.</p>
            ''')
    browser.setHtml(text)
    browser.setOpenExternalLinks(True)
    return browser


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QW.QApplication.instance()
    if not qapp:
        qapp = QW.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    qapp.exec_()