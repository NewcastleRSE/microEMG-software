#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:10:56 2024

@author: Gabrielle
"""

import sys
import os

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile

import microemggui

from microemggui.widgets.preproc.preproc_step import PreprocWidget
from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.models.emg import EMGDataModel

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
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
        raw_emg_data_model = EMGDataModel(emg_data)

        # Create preprocessing settings and model - will eventually add via method
        # TODO: set default filter specification settings (and/or initial values for
        # GUI widgets)
        settings = EMGPreprocSettings()
        settings.add_remove_mains()  # Remain mains noise
        settings.add_butterworth_filter(
            filter_type="highpass", cutoff_freq=100, apply_filter=False
        )

        self.settings_model = EMGPreprocSettingsModel(settings)
        print("INITIAL SETTINGS")
        self.settings_model.settings.print_settings()

        # colors
        # avoiding red (reserving for indicating bad channels)
        clrs = Prism_10.hex_colors
        clrs = [clrs[i] for i in [0, 4, 1, 5]]  # purple, green, blue, yellow
        # clrs = [clrs[1]] # only dark blue

        # Preprocessing widdget
        self.widget = PreprocWidget(
            raw_emg_data_model, self.settings_model, emg_clrs=clrs, parent=self
        )

        # signal for verifying settings update
        self.widget.widgets["settings"].settings_changed.connect(
            self.main_window_settings
        )

        self.setCentralWidget(self.widget)

    def main_window_settings(self):
        # slot for verifying settings update
        print("MAIN WINDOW UPDATED SETTINGS")
        self.settings_model.settings.print_settings()


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
