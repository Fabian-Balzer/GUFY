## GUFY - GUI for FLASH Code simulations based on yt [Version 1.0]
GUFY is a graphical user interface intended for a quick and easy overview on simulated (FLASH-)datasets
by visualizing them using the tools provided by [**yt project**](https://yt-project.org/).

### Features:
* Simple file loading in **Single file** or **Time series** mode
* Easy access to the extrema and units of the fields to be used
* Supports five different plot modes with basic settings for each:
  * Slice plots (Axis-aligned and off-axis)
  * Projection plots (Axis-aligned and off-axis)
  * Line plots
  * Phase plots
  * Profile plots (For one or two fields at multiple times, having time as x-Axis)
  * Particle plots (In a very basic form)
* Several annotation options, especially for slice and projection in cartesian geometries
* Easy access to adding custom derived fields
* Writing produced plots or just some settings to a script to reproduce and enhance them later
* Interactive design with logging and default configuration settings

### Setup instructions:
- Download the folder named GUFY
- Install all required python modules (see below)
- To run GUFY on your computer, navigate to the folder and execute _GUFY.py_ with python using
`$ python ytGUI.py `
- To run GUFY on a server, use
`$ ssh -X <SERVERNAME>`
  to log in and then execute the program

### Requirements:
The following versions of python and packages need to be installed prior to using GUFY:
- [**Python** (version 3.6 or higher)](https://www.python.org/downloads/)
- [**yt** (version 3.5 or higher)](https://yt-project.org/doc/installing.html)
- [**PyQt** (version 5.9 or higher)](https://www.riverbankcomputing.com/software/pyqt/download5)

### Contact:
If you find any bugs or the setup doesn't work, please contact me: fabian.balzer@studium.uni-hamburg.de

#### Notes:
Developed by Fabian Balzer based on the project math2.py by Jannik Schilling, September 2019

---

## Copyright:
GUFY - Copyright (c) 2019, Fabian Balzer

Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE.txt, distributed with this software.

---
