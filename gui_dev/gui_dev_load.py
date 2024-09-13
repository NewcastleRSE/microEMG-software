#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for using the GUI to load data
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from microemggui.styles.gui_style import get_formatted_gui_style_sheet
from microemggui.widgets.load.load_step import LoadWidget

# %%


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Preprocessing widdget
        self.widget = LoadWidget(parent=self)

        self.setCentralWidget(self.widget)

        self.resize(400, 600)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Apply style
gui_style_sheet = get_formatted_gui_style_sheet()
app.setStyleSheet(gui_style_sheet)

app.exec()
