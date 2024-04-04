#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script for EMG time series visualisation widget.
"""


import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile

import microemggui
import microemggui.widgets.emg_viewer as ev
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
        self.w = ev.EMGViewerWidget(emg_data_model, parent=self)
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
