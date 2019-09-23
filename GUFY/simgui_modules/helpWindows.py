# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.
-------------------------------------------------------------------------------

@author: Fabian Balzer (fabian.balzer@studium.uni-hamburg.de)

Module containing the functions and widgets to open small help windows.
"""


import PyQt5.QtWidgets as QW
import PyQt5.QtGui as QG
import PyQt5.QtCore as QC


helpKeys = ["derived fields", "line plots", "slice plots", "phase plots",
            "profile plots", "projection plots", "FAQ", "License"]
helpTexts = [
"""<p>When defining a new derived field, you need to give it a
<strong>new field name</strong> that's unknown to yt.</p>

<p>The display name is used when yt tries to display the fields' name on the
axis of a plot. You may use matplotlibs <strong>mathtext</strong> for the
display name. Upon plotting, this text is put into a
<i>r"$\\rm{DISPLAYNAME}$"</i>-environment.
For detailed information click
<a href="https://matplotlib.org/users/mathtext.html">here</a>.</p>

<p>You then need to give yt a valid function with <strong>field</strong> and
<strong>data</strong> as the arguments, where the field is just a yt-internal
decoy and the data is containing the data to plot (i.e.
<font color="green">ds.all_data()</font> or <font color="green">ds.sphere()
</font>). See below for an example utilizing yt's unit system and numpy.</p>
<p>The TextEdit for the input of this dialog does an automatic check if your
function is readable with python and doesn't contain any name errors.
yt and numpy as np are already imported and ready for use.<br>
<b>Hint:</b> The function is executed once the focus is changed to prevent
errors, or if you press <i>CTRL+Return</i>. This way, you may use something
like <i>print(dir(yt.units.physical_constants))</i> inside
of the function and press <i>CTRL+Return</i> to receive
the available physical constants, or use <i>print(yt.units.msun)</i> to
receive values. Instead of <i>print()</i>, using <i>GUILogger.info()</i>
is also an option to have the result logged. Try <i>GUILogger.info("Hi")</i> 
to get a feeling for it.</p>

<p>Lastly, the Unit LineEdit checks the <strong>output unit</strong> of the
function for you. In some cases, the unit might be incorrect.</p>
<p>If so, try multiplying the value with a <font color="green">yt.unit.YOURUNIT
</font> until it fits.
You can also use 'auto' as a unit. In this case the dimensionality is
automatically set.</p>

<p>If you have made a mistake when defining a custom field, you may <b>force an
override</b>. If you are about to do overwrite an existing field, the text for
the field name turns yellow.
I would only recommend doing that if you know what you are doing.
</p>

<p>For detailed information on derived fields click
<a href="https://yt-project.org/doc/developing/creating_derived_fields.html">
here</a>.</p>
<p><b>Worked example for a function:</b> Calculating the sound speed:<br>
<center>
<img src="simgui_registry/soundSpeedExample.png">
</center>
</p>""",
"""<p><b>Line plots</b> are a special case of 1D Profile plots.</p>

<p>For the data, the requested field for the vertical axis is sampled at
n=512 evenly spaced points between two spacial points in the the dataset
provided through <b>Start point</b> and <b>End point</b>.</p>
<p>To change the number of sampling points or to plot multiple fields over the
same line, please use <b>Write settings to script</b> button and modify the
script accordingly.</p>

<p>For detailed information on line plots click
<a href="https://yt-project.org/doc/visualizing/plots.html#d-line-sampling">
here</a>.<br>For a simple example click
<a href="https://yt-project.org/doc/cookbook/simple_plots.html#simple-1d-line-plotting">
here</a>.</p>""",
"""<p><b>Slice plots</b> display the distribution of a field through a 2D-Slice
of the dataset using a color scheme.</p>

<p>yt features both slice plots with a gridaxis aligned and an off-axis normal
vector.<br>
The normal vector mode, i.e. axis-aligned or off-axis, can be selected in
the <b>Normal vector options</b>.<br>
For axis-aligned normal vectors, an axis can be chosen in the ComboBox.<br>
For off-axis normal vectors, the x, y and z coordinate of the vector may be
specified, along with the x, y and z coordinates of the north vector, a vector
which will define the 'up'-direction.<br>
Note that hints for the width can only be given while in axis-aligned mode.
</p>

<p>Right next to that are the general options for slice plots, which include
setting the <b>Grid Unit</b> of the spacial axes, the coordinates the plot is
<b>centered around</b>, the <b>horizontal</b> and <b>vertical width</b> and an
option to <b>zoom</b> in. The center coordinate that's the same as the normal
axis can be used to set the height the slice is taken at.<br>
<font color="red">Warning:</font> If you are using <b>zoom</b>, it will be
called after setting the width and thus alter it.</p>

<p>The <b>Colorbar</b> options include a LineEdit <b>Colors</b> for the color
scheme with a check for availability. Apart from <i>viridis</i>, I can
recommend <i>dusk, hot and bwr</i>. <i>doom</i> also produces... interesting plots.
The _r-suffix means that the colors are reversed. Log scaling may be applied
even for negative minimum values, in which case a symlog scaling will be used.
</p>

<p>For detailed information on slice plots click
<a href="https://yt-project.org/doc/visualizing/plots.html#slices-projections">
here</a>.<br>For a simple example with modification suggestions click
<a href="https://yt-project.org/doc/cookbook/simple_plots.html#accessing-and-modifying-plots-directly">
here</a>.</p>
""",
"""<p><b>Phase plots</b> can display the distribution of a field with respect
to two binning fields.</p>

<p>This field may be weighted using a weight field as well, and is visualized
using a color scheme.<br>
<font color="red">Warning:</font> If the weight field is set to <b>None</b>,
the extrema calculated will be incorrect.<br>
For phase plots, yt's default of 128 x 128 bins is used because this is usually
enough. If another specification is wished, you could write the settings to
script and change <i>x_bins</i> and <i>y_bins</i> manually.<br>
You may set the field, extrema, units and log scaling individually for each
axis. Log scaling may be applied only for positive values.</p>

<p>The <b>Colorbar</b> options also include a LineEdit <b>Colors</b> for the
color scheme with a check for availability. Apart from <i>viridis</i>, I can
recommend <i>dusk, hot and bwr</i>. <i>doom</i> also produces... interesting
plots. The _r-suffix means that the colors are reversed.</p>

<p>
With the <i>fractional</i>-keyword, phase plots can also be turned fractional.
<br>To plot particle fields as phase plots, check the <i>Particle plot</i>
CheckBox. This will replace the gas fields for each axis with particle fields.
</p>

<p>For detailed information on phase plots click
<a href="https://yt-project.org/doc/visualizing/plots.html#d-phase-plots">here
</a>.<br>For an advanced example for customizing phase plots click
<a href="https://yt-project.org/doc/cookbook/complex_plots.html#customized-phase-plot">
here</a>.</p>
""",
"""<p><b>Profile plots</b> sample one field with respect to another, using bins
for the field on the x-axis.</p>

<p>These bins can be weighted with a <b>weight field</b> set in the <b>Profile
plot options</b>.<br>
<font color="red">Warning:</font> If the weight field is set to <b>None</b>,
the extrema calculated will be incorrect.<br>
For the profiles, yt's default of 64 bins is used because this is usually
enough. If another specification is wished, you could write the settings to
script and change <i>n_bins</i> manually.<br>
By writing everything to script, the plot type could also be changed to a
histogram instead of a continuous line.<br>
With the <i>fractional</i>-keyword, profile plots can also be turned fractional.
</p>

<p>If a valid profile plot (with only one profile) has been produced a second
profile may be added. Just check the CheckBox for that. This will freeze the
<b>Horizontal</b> options.<br>
<font color="red">Warning:</font> This feature has not been implemented for
script writing and restoring plot settings.</p>

<p>If a time series is loaded, <b>time</b> can be selected for the x-axis. You
may then choose the quantity that is calculated of the y-field for each loaded
file. Because the calculation takes some time, the data points corresponding to
a time and quantity are saved so they don't have to be computed again if you
change the title, extrema or log scaling.<br>
Also, you may plot profiles for every nth file of the series by checking the
corresponding checkbox. You can modify n by scrolling or using the up- and
down-arrows.</p>

<p>For detailed information on profile plots click
<a href="https://yt-project.org/doc/visualizing/plots.html#d-profile-plots">
here</a>.<br>
For a simple example for a profile over time click
<a href="https://yt-project.org/doc/cookbook/simple_plots.html#d-profiles-over-time">
here</a>.<br>
For an advanced example for customizing profile plots click
<a href="https://yt-project.org/doc/cookbook/complex_plots.html#customized-profile-plot">
here</a></p>
""",
"""<p><b>Projection plots</b> display the distribution of a field along a line of
sight. This distribution can be weighted by a <b>weight field</b>.</p>

<p>yt features both projection plots with a gridaxis aligned and an
off-axis normal vector.<br>
The normal vector mode, i.e. axis-aligned or off-axis, can be selected in
the <b>Normal vector options</b>.<br>
For axis-aligned normal vectors, an axis can be chosen in the ComboBox.<br>
For off-axis normal vectors, the x, y and z coordinate of the vector may be
specified, along with the x, y and z coordinates of the north vector, a vector
which will define the 'up'-direction.<br>
Note that hints for the width can only be given while in axis-aligned mode.</p>

<p>Right next to that are the general options for projection plots, which include
setting the <b>Grid Unit</b> of the spacial axes, the coordinates the plot is
<b>centered around</b>, the <b>horizontal</b> and <b>vertical width</b> and an
option to <b>zoom</b> in. Changing the center coordinate that's the same as the
normal axis will not have any effect on the plot.<br>
<font color="red">Warning:</font> If you are using <b>zoom</b>, it will be
called after setting the width and thus alter it.</p>

<p>The <b>Colorbar</b> options include a LineEdit <b>Colors</b> for the color
scheme with a check for availability. Apart from <i>viridis</i>, I can
recommend <i>dusk, hot and bwr</i>.
<i>doom</i> also produces... interesting plots.
The _r-suffix means that the colors are reversed.
Log scaling may be applied even for negative minimum values, in which case a
symlog scaling will be used.<br>
The specified <b>weight field</b> determines what the integration will be
weighted with. If set to None, no weighting will be applied, and new extrema
have to be calculated. If you're using an axis-aligned normal vector, in this
case, you may also check the <b>Divide by height</b> CheckBox which will
do exactly what it says.</p>

<p>To project particle data, check the <i>Particle plot</i>
CheckBox. This will replace the gas fields for each axis with particle fields.
<br><b>Note:</b> This feature is disabled for cylindrical datasets</p>

<p>For detailed information on projection plots click
<a href="https://yt-project.org/doc/visualizing/plots.html#projection-plots">
here</a>.<br>For a simple example with an off-axis projection click
<a href="https://yt-project.org/doc/cookbook/simple_plots.html#off-axis-projection">
here</a>.<br>For an example where only a slice of the domain is projected, click
<a href="https://yt-project.org/doc/cookbook/complex_plots.html#thin-slice-projections">
here</a>.</p>
""",
"""<p><b>Frequently asked questions:</b>
</p><p><ins>
- What does <b>Restore plot settings</b> do?
</ins></p><p style="text-align: justify; margin-left:30px;">
    When pressing this button, you are recovering the state the GUI was in when
    the plot shown was made.<br>
    In addition to that, any navigational changes you have made,
    i.e. zooming and panning, are read and set as well. This includes center
    coordinates and width for slice and projection plots, and axes boundaries
    for line, phase, and profile plots.
</p><p><ins>
- Which color scheme should I use?
</ins></p><p style="text-align: justify; margin-left:30px;">
    There are loads of color schemes available - a great overview is given
<a href="https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html">on this
website</a> by the matplotlib module. Usually, <i>viridis, plasma, inferno,
magma</i> and <i>cividis</i> work best since they even work when the plot is
converted to grayscale.
</p><p><ins>
- Why can't I add a derived field without a loaded dataset?
</ins></p><p style="text-align: justify; margin-left:30px;">
    To avoid errors, a sample point of the loaded dataset is needed to run the
    function with.
</p><p><ins>
- Why does it take such a long time to cancel a plotting process?
</ins></p><p style="text-align: justify; margin-left:30px;">
    Pressing the cancel-button will finish the current step in plotting since I
    don't have any access to the yt-internal functions. That's why sometimes
    the plot may still be drawn onto the canvas.
</p><p><ins>
- Why does the first plot of a time series usually load faster?
</ins></p><p style="text-align: justify; margin-left:30px;">
    When scanning the file for derived fields, it is already loaded into memory.
</p><p><ins>
- Why should I recalculate the extrema in <b>Time series</b> mode?
</ins></p><p style="text-align: justify; margin-left:30px;">
    Over the course of a simulation, the extrema of the fields may change.
    In some simulations, a uniform temperature distribution might be conveyed
    for the first file, so after finding that out, you can select i.e. the last
    file and recalculate the extrema there.
</p><p>
<b>Please write an email to fabian.balzer@studium.uni-hamburg.de
with more suggestions for questions.
</p>
""",
"""<p>This software is freely available at
<a href="https://github.com/Fabian-Balzer/GUFY">https://github.com/Fabian-Balzer/GUFY</a>.</p>
<p>GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.</p>
"""]

helpTextDict = dict(zip(helpKeys, helpTexts))


class HelpWindow(QW.QDialog):
    """A window containing some information for help."""
    def __init__(self, key, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(700, 600)
        self.setWindowIcon(QG.QIcon('simgui_registry/CoverIcon.png'))
        self.setWindowTitle(f"Help on {key}")
        if key == "FAQ":
            self.setWindowTitle("Frequently asked questions")
        if key == "License":
            self.setWindowTitle("License")
        self.Display = QW.QTextBrowser(self)
        text = helpTextDict[key]
        self.Display.setGeometry(0, 0, 700, 600)
        self.Display.setOpenExternalLinks(True)
        self.Display.setHtml(text)
        self.Display.setReadOnly(True)
