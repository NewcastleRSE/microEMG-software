#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for EMG time series visualisation widget.
"""


import sys

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import QApplication, QMainWindow

from microemggui.widgets.emg_viewer import EMGViewerWidget
from microemggui.models.emg import EMGDataRawModel
from microemggui.styles.gui_style import get_formatted_gui_style_sheet

from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # EMG data
        recording_num = 0
        emg_dir, _ = cfg.get_recording_path_and_id(recording_num)
        emg_files = EMGFiles(emg_dir)
        emg_data = emg_files.load_emg_data()
        emg_data_model = EMGDataRawModel(emg_data)

        # colors
        # avoiding red (reserving for indicating bad channels)
        clrs = Prism_10.hex_colors
        # clrs = [clrs[i] for i in [0, 4, 1, 5]]  # purple, green, blue, yellow
        # clrs = [clrs[i] for i in [1, 2]] # dark blue, light blue
        # clrs = [clrs[i] for i in [1, 8]] # dark blue, pink-purple
        # clrs = [clrs[1]] # only dark blue

        self.w = EMGViewerWidget(emg_data_model, clrs, parent=self)
        self.setCentralWidget(self.w)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Apply style
gui_style_sheet = get_formatted_gui_style_sheet()
app.setStyleSheet(gui_style_sheet)


app.exec()
