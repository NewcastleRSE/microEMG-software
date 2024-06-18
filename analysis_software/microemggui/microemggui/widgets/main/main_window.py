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
    QPushButton,
    QButtonGroup,
    QVBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from microemggui.widgets.base import (
    AnalysisToolbarButton,
    AnalysisToolbarLabel,
    SectionTitle,
    ExpandingVSpacer,
)

# --- Widgets for main window ---


class MicroEMGLogo(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Button icon
        # TODO: set resource path or otherwise define path for icons
        icon_dir = os.path.join(
            "analysis_software",
            "microemggui",
            "microemggui",
            "icons",
            "bootstrap-icons-1.11.3",
        )
        logo_icon = "activity.svg"

        self.setIcon(QIcon(os.path.join(icon_dir, logo_icon)))
        self.setStatusTip("Home")
        self.setCheckable(True)


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
            "exporttext": "Export results",
            "exportbutton": "Export",
        }

        toolbar_w_is_button = [
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            False,
            True,
        ]

        # Create and add widgets
        self.widgets = {}
        button_group = QButtonGroup(
            self
        )  # exclusive group so can only click one at a time

        # First add logo button
        self.widgets["logo"] = MicroEMGLogo(parent=self)
        self.addWidget(self.widgets["logo"])
        button_group.addButton(self.widgets["logo"])

        # Add analysis step buttons and section labels
        for (w_name, text), button in zip(toolbar_w_text.items(), toolbar_w_is_button):
            if button:  # Create buttons
                self.widgets[w_name] = AnalysisToolbarButton(text, parent=self)
                self.widgets[w_name].setEnabled(False)  # Disable buttons at start
                self.widgets[w_name].setCheckable(True)  # Add checked state
                button_group.addButton(self.widgets[w_name])  # Add to button group
            else:  # Create section labels
                self.widgets[w_name] = AnalysisToolbarLabel(text, parent=self)
            self.addWidget(self.widgets[w_name])  # Add widget to toolbar

        # Initial button states
        self.widgets["loadbutton"].setEnabled(True)  # Enable first step (loading)
        self.widgets["logo"].toggle()

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
        layout.setContentsMargins(20, 0, 0, 0)
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
    # Main window for microEMG GUI

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
