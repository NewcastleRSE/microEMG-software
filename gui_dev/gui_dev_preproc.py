#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:10:56 2024

@author: Gabrielle
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from microemggui.widgets.preproc.filter_settings import FilterSettingsWidget
from microemggui.formatting import StyleSettings


class MainWindow(QMainWindow):
    def __init__(self, style_settings):
        super().__init__()

        self.filter_settings_widget = FilterSettingsWidget(style_settings)

        self.setCentralWidget(self.filter_settings_widget)


style_settings = StyleSettings(h_major=40, h_minor=20)

app = QApplication(sys.argv)
window = MainWindow(style_settings=style_settings)
window.show()

app.exec()
