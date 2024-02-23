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

from microemggui.widgets.preproc.preproc_settings import PreprocSettingsWidget
from microemggui.models.settings import EMGPreprocSettingsModel
from pymicroemg.emg_preproc_settings import EMGPreprocSettings

# %%

settings = EMGPreprocSettings()
settings.add_butterworth_filter()

settings.print_settings()

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create preprocessing settings and model - will eventually add via method
        settings = EMGPreprocSettings()
        settings.add_remove_mains()  # Remain mains noise
        settings.add_butterworth_filter()

        self.settings_model = EMGPreprocSettingsModel(settings)
        print("INITIAL SETTINGS")
        self.settings_model.settings.print_settings()

        # Create preprocessing settings widget
        self.widget = PreprocSettingsWidget(self.settings_model, parent=self)
        # signal for verifying settings update
        self.widget.settings_changed.connect(self.main_window_settings)

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
