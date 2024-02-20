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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = PreprocSettingsWidget()

        self.setCentralWidget(self.widget)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# style
style_dir = microemggui.__file__
style_dir = style_dir[:-11]  # remove init
style_path = os.path.join(style_dir, "styles", "style.qss")
gui_style_file = QFile(style_path)
gui_style_file.open(QFile.OpenModeFlag.ReadOnly)
gui_style = gui_style_file.readAll().toStdString()
app.setStyleSheet(gui_style)


app.exec()
