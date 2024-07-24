#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:10:56 2024

@author: Gabrielle
"""

import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile

import microemggui

from microemggui.widgets.findmu.find_mu_step import FindMUWidget
from microemggui.models.settings import EMGAnalysisMotorUnitSettingsModel
from microemggui.models.emg import EMGAnalysisReconstructModel

from pymicroemg.emg_reconstruct import EMGAnalysisReconstruct
from pymicroemg.emg_reconstruct_settings import (
    EMGAnalysisMotorUnitSettings,
    EMGAnalysisReconstructSettings,
)
from pymicroemg.emg_preproc_settings import EMGPreprocSettings
from pymicroemg.emg_files import EMGFiles
import pymicroemg.helper_config as cfg

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # EMG
        recording_num = 1
        emg_dir, _ = cfg.get_control_recording_path_and_id(recording_num)
        emg_files = EMGFiles(emg_dir)
        emg_data = emg_files.load_emg_data()
        emg_data.trim_emg_ts(0, 30)

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
        mu_settings_model = EMGAnalysisMotorUnitSettingsModel(mu_settings)

        # prep reconstruction analysis
        recon_settings = EMGAnalysisReconstructSettings()
        reconstruct = EMGAnalysisReconstruct(preproc_emg_data, mu_settings, recon_settings)
        reconstruct_model = EMGAnalysisReconstructModel(reconstruct)

        # MU widdget
        self.widget = FindMUWidget(mu_settings_model, reconstruct_model, parent=self)

        # layout and size
        self.setCentralWidget(self.widget)
        self.resize(1200, 850)


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
