#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:10:56 2024

@author: Gabrielle
"""

import sys

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import QApplication, QMainWindow

from microemggui.widgets.preproc.preproc_step import PreprocWidget
from microemggui.models.settings import EMGPreprocSettingsModel
from microemggui.models.emg import EMGDataRawModel
from microemggui.styles.gui_style import get_formatted_gui_style_sheet

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
        raw_emg_data_model = EMGDataRawModel(emg_data)

        # Create preprocessing settings and model - will eventually add via method
        settings = EMGPreprocSettings()
        settings.add_remove_mains()  # Remain mains noise
        settings.add_butterworth_filter(
            filter_type="bandpass", cutoff_freq=[100, 2000], apply_filter=True
        )

        self.settings_model = EMGPreprocSettingsModel(settings)
        print("INITIAL SETTINGS")
        self.settings_model.settings.print_settings()

        # colors
        # avoiding red (reserving for indicating bad channels)
        clrs = Prism_10.hex_colors
        # clrs = [clrs[i] for i in [0, 4, 1, 5]]  # purple, green, blue, yellow
        # clrs = [clrs[1]] # only dark blue

        # Preprocessing widdget
        self.widget = PreprocWidget(
            raw_emg_data_model, self.settings_model, emg_clrs=clrs, parent=self
        )

        # signal for verifying settings update
        self.widget.widgets["settings"].settings_valid.connect(self.main_window_settings)

        self.setCentralWidget(self.widget)

        self.resize(1200, 850)

    def main_window_settings(self, settings_valid):
        # slot for verifying settings update
        print(f"MAIN WINDOW UPDATED SETTINGS (valid = {settings_valid})")
        self.settings_model.settings.print_settings()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Apply style
gui_style_sheet = get_formatted_gui_style_sheet()
app.setStyleSheet(gui_style_sheet)


app.exec()
