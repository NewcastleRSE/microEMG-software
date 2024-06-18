#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for main window with toolbars and other navigation elements.

"""

import os

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QToolBar,
    QLabel,
    QVBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from microemggui.widgets.base import (
    AnalysisToolbarButton,
    SectionTitle,
    ExpandingVSpacer,
)

# --- Widgets for main window ---


class AnalysisToolbar(QToolBar):
    # Toolbar on left of window for navigating analysis steps

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
                self.widgets[w] = AnalysisToolbarButton(text, parent=self)
            else:
                self.widgets[w] = QLabel(text, parent=self)

            self.addWidget(self.widgets[w])

        # Toolbar properties
        self.setMovable(False)
        self.setOrientation(Qt.Vertical)


class WelcomeWidget(QWidget):
    # Widget for welcome page

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


class TopToolbar(QToolBar):
    # Toolbar on top of page for settings, info, and help links
    # Also has label for recording

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add placehold label for recording
        # TODO: replace with custom label class
        self.widgets = {"recording": QLabel("Recording:", parent=self)}
        size_policy = self.widgets["recording"].sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Expanding)
        self.widgets["recording"].setSizePolicy(size_policy)

        for w in self.widgets.values():
            self.addWidget(w)

        # Icons for actions
        # TODO: set resource path or otherwise define path for icons
        icon_dir = os.path.join(
            "analysis_software",
            "microemggui",
            "microemggui",
            "icons",
            "bootstrap-icons-1.11.3",
        )
        icons = ["gear.svg", "question-circle.svg", "info-circle.svg"]

        tips = ["Settings", "Help", "About"]

        for icon, tip in zip(icons, tips):
            action = QAction(QIcon(os.path.join(icon_dir, icon)), tip, self)
            action.setStatusTip(tip)
            # TODO: create and connect to pop-up windows
            self.addAction(action)

        # Properties
        self.setIconSize(QSize(16, 16))


# --- Main window ---


class MicroEMGMain(QMainWindow):
    def __init__(self):
        super().__init__()

        toolbar = AnalysisToolbar("Analysis toolbar")

        # Add toolbar to window
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(TopToolbar(parent=self))
        layout.addWidget(WelcomeWidget(parent=self))
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # Add widget to center
        # widget = WelcomeWidget(parent=self)
        self.setCentralWidget(widget)

        # Window properties
        self.resize(1200, 800)
