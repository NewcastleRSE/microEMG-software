#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load and execute full microEMG GUI
"""

import sys

from PySide6.QtWidgets import QApplication

from microemggui.widgets.main.main_window import MicroEMGMain
from microemggui.styles.gui_style import get_formatted_gui_style_sheet

# %% Create and execute GUI

app = QApplication(sys.argv)
window = MicroEMGMain()
window.show()

# Apply style
gui_style_sheet = get_formatted_gui_style_sheet()
app.setStyleSheet(gui_style_sheet)

app.exec()
