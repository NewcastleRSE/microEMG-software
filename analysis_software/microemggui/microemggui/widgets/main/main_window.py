#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for main window with toolbars and other navigation elements.

"""


from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QLabel
from PySide6.QtCore import Qt

from microemggui.widgets.base import MainToolbarButton


class MicroEMGMain(QMainWindow):
    def __init__(self):
        super().__init__()

        # Info about widgets to add to toolbar
        toolbar_w_text = {
            "preptext": "Prepare EMG",
            "loadbutton": "1. Load",
            "preprocbutton": "2. Preprocess",
            "selectbutton": "3. Select data",
            "analysetext": "Analyse EMG",
            "mubutton": "4. Find motor units",
            "fibresbutton": "5. Localise fibres",
            "jitterbutton": "6. Compute jitter",
        }

        toolbar_w_is_button = [False, True, True, True, False, True, True, True]

        # Create toolbar and add widgets
        toolbar_widgets = {}
        toolbar = QToolBar("Analysis toolbar")
        for (w, text), button in zip(toolbar_w_text.items(), toolbar_w_is_button):
            if button:
                toolbar_widgets[w] = MainToolbarButton(text, parent=self)
            else:
                toolbar_widgets[w] = QLabel(text, parent=self)

            toolbar.addWidget(toolbar_widgets[w])

        # Toolbar properties
        # toolbar.setMovable(False)

        widget = QWidget(parent=self)

        # Add toolbar to window
        self.addToolBar(toolbar)
        toolbar.setOrientation(Qt.Vertical)
        self.setCentralWidget(widget)

        # Window properties
        self.resize(800, 800)
