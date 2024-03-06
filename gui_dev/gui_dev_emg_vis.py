#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for EMG time series visualisation widget.
"""


import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PySide6.QtCore import QFile

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import microemggui
from microemggui.widgets.emg_viewer import StartTimeWidget
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

        # make figure
        fig, _ = emg_data.plot_emg_ts(start_t=0, stop_t=1, downsample_factor=10)

        # figure widget
        self.emg_vis = FigureCanvasQTAgg(fig)

        # controls widget
        self.controls_w = StartTimeWidget(self)

        layout = QVBoxLayout()
        layout.addWidget(self.emg_vis)
        layout.addWidget(self.controls_w)
        # layout.setContentsMargins(0, 0, 0, 0)

        # self.setLayout(layout)

        self.setCentralWidget(self.controls_w)


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
