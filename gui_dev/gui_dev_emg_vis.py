#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for EMG time series visualisation widget.
"""


import sys
import os

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile

import microemggui
from microemggui.widgets.emg_viewer import EMGViewerWidget
from microemggui.models.emg import EMGDataModel
from pymicroemg.emg_files import EMGFiles

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # EMG data
        recording_ID = "Stuart_E2"
        emg_dir = os.path.join(
            "data", "sample_data_20231124", "real", recording_ID, "raw"
        )
        emg_files = EMGFiles(emg_dir)
        emg_data = emg_files.load_emg_data()
        emg_data_model = EMGDataModel(emg_data)

        # colors
        # avoiding red (reserving for indicating bad channels)
        clrs = Prism_10.hex_colors
        clrs = [clrs[i] for i in [0, 4, 1, 5]]  # purple, green, blue, yellow
        # clrs = [clrs[i] for i in [1, 2]] # dark blue, light blue
        # clrs = [clrs[i] for i in [1, 8]] # dark blue, pink-purple
        # clrs = [clrs[1]] # only dark blue

        self.w = EMGViewerWidget(emg_data_model, clrs, parent=self)
        self.setCentralWidget(self.w)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# style
# TODO: create function for loading and applying style
style_dir = microemggui.__file__
style_dir = style_dir[:-11]  # remove init
style_path = os.path.join(style_dir, "styles", "style.qss")
gui_style_file = QFile(style_path)
gui_style_file.open(QFile.OpenModeFlag.ReadOnly)
gui_style = gui_style_file.readAll().toStdString()
app.setStyleSheet(gui_style)


app.exec()
