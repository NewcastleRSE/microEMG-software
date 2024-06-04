#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for using the GUI to load data
"""

import sys
import os


from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile

import microemggui

from microemggui.widgets.load.load_step import LoadWidget

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Preprocessing widdget
        self.widget = LoadWidget(parent=self)

        self.setCentralWidget(self.widget)

        self.resize(300, 300)


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
