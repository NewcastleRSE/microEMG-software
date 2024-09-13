#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates channel selection widget for GUI development and testing.
"""

import sys

from palettable.cartocolors.qualitative import Prism_10

from PySide6.QtWidgets import QApplication, QMainWindow

from microemggui.models.emg import EMGDataRawModel, EMGDataPreprocModel
from microemggui.widgets.channels.channels_step import ChannelsWidget
from microemggui.styles.gui_style import get_formatted_gui_style_sheet

from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Raw EMG data
        recording_num = 0
        emg_dir, _ = cfg.get_recording_path_and_id(recording_num)
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

# Apply style
gui_style_sheet = get_formatted_gui_style_sheet()
app.setStyleSheet(gui_style_sheet)

app.exec()
