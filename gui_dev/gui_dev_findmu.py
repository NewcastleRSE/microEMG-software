#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:10:56 2024

@author: Gabrielle
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from microemggui.widgets.findmu.find_mu_step import FindMUWidget
from microemggui.models.emg import EMGAnalysisReconstructModel
from microemggui.styles.gui_style import get_formatted_gui_style_sheet

from pymicroemg.emg_reconstruct_settings import (
    EMGAnalysisMotorUnitSettings,
    EMGAnalysisReconstructSettings,
    EMGAnalysisMotorUnitJitterSettings,
    EMGAnalysisMotorUnitClusterSettings,
)
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # EMG
        recording_num = 0
        emg_dir, _ = cfg.get_recording_path_and_id(recording_num)
        emg_files = EMGFiles(emg_dir)
        emg_data = emg_files.load_emg_data()
        emg_data.trim_emg_ts(0, 60)

        settings = EMGPreprocSettings()
        settings.add_remove_mains()  # Remain mains noise
        settings.add_butterworth_filter(
            filter_type="bandpass", cutoff_freq=[100, 2000], apply_filter=True
        )
        preproc_emg_data = emg_data.preprocess(settings)

        # Motor unit settings
        mu_settings = EMGAnalysisMotorUnitSettings()
        mu_settings.tk_filt_thres_PsC = 0.05
        mu_settings.tk_filt_thres_spike = 0.15

        # prep reconstruction analysis
        recon_settings = EMGAnalysisReconstructSettings()
        mu_cluster_settings = EMGAnalysisMotorUnitClusterSettings()
        mu_jitter_settings = EMGAnalysisMotorUnitJitterSettings()
        reconstruct = preproc_emg_data.set_up_reconstruct_analysis(
            mu_settings=mu_settings,
            recon_settings=recon_settings,
            mu_cluster_settings=mu_cluster_settings,
            mu_jitter_settings=mu_jitter_settings,
        )
        reconstruct_model = EMGAnalysisReconstructModel(reconstruct)

        # MU widdget
        self.widget = FindMUWidget(reconstruct_model, parent=self)

        # layout and size
        self.setCentralWidget(self.widget)
        self.resize(1200, 850)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Apply style
gui_style_sheet = get_formatted_gui_style_sheet()
app.setStyleSheet(gui_style_sheet)


app.exec()
