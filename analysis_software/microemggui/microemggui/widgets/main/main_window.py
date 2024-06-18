#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for main window with toolbars and other navigation elements.

"""


from PySide6.QtWidgets import QMainWindow, QWidget, QToolBar, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

from microemggui.widgets.base import MainToolbarButton, SectionTitle, ExpandingVSpacer

# --- Widgets for main window ---


class AnalysisToolbar(QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        # Add widgets
        self.widgets = {}

        for (w, text), button in zip(toolbar_w_text.items(), toolbar_w_is_button):
            if button:
                self.widgets[w] = MainToolbarButton(text, parent=self)
            else:
                self.widgets[w] = QLabel(text, parent=self)

            self.addWidget(self.widgets[w])

        # Toolbar properties
        self.setMovable(False)
        self.setOrientation(Qt.Vertical)


class WelcomeWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create widgets
        self.widgets = {
            "title": SectionTitle("Welcome to the microEMG analysis GUI", parent=self)
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # spacer
        layout.setContentsMargins(10, 0, 0, 0)
        self.setLayout(layout)


# --- Main window ---


class MicroEMGMain(QMainWindow):
    def __init__(self):
        super().__init__()

        toolbar = AnalysisToolbar("Analysis toolbar")

        # Add toolbar to window
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # Add widget to center
        widget = WelcomeWidget(parent=self)
        self.setCentralWidget(widget)

        # Window properties
        self.resize(1200, 800)
