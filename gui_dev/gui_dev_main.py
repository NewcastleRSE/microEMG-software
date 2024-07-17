#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 17:03:56 2024

@author: Gabrielle
"""

import sys
import os


from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile

import microemggui

from microemggui.widgets.main.main_window import MicroEMGMain

# %%


app = QApplication(sys.argv)
window = MicroEMGMain()
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
