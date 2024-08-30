#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates channel selection widget for GUI development and testing.
"""

import sys
import os

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile

import microemggui

from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.widgets.channels.channels_step import ChannelsWidget

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Raw EMG data
        recording_num = 1
        emg_dir, _ = cfg.get_control_recording_path_and_id(recording_num)
        emg_files = EMGFiles(emg_dir)
        emg_data = emg_files.load_emg_data()
        emg_data.trim_emg_ts(0, 30)
        raw_emg_model = EMGDataRawModel(emg_data)

        # Preprocessing settings and model
        settings = EMGPreprocSettings()
        settings.add_remove_mains()  # Remain mains noise
        settings.add_butterworth_filter(
            filter_type="bandpass", cutoff_freq=[100, 2000], apply_filter=True
        )

        # Preprocessed data
        emg_data_preproc = emg_data.preprocess(settings)
        preproc_emg_model = EMGDataPreprocModel(emg_data_preproc)

        # colors
        emg_clrs = Prism_10.hex_colors

        # Channels widdget
        self.widget = ChannelsWidget(raw_emg_model, preproc_emg_model, emg_clrs)

        self.setCentralWidget(self.widget)

        self.resize(1100, 750)


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
