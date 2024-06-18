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
    QStackedLayout,
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
from microemggui.widgets.load.load_step import LoadWidget

# from microemggui.widgets.preproc.preproc_step import PreprocWidget

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
            "load": "1. Load",
            "preprocess": "2. Preprocess",
            "select": "3. Select data",
            "analysetext": "Analyse EMG",
            "motorunits": "4. Find motor units",
            "fibres": "5. Localise fibres",
            "jitter": "6. Compute jitter",
            "exporttext": "Export results",
            "export": "Export",
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
        button_group = QButtonGroup(self)  # group so can only click one at a time

        # First add logo button for home page
        self.widgets["home"] = MicroEMGLogo(parent=self)
        self.addWidget(self.widgets["home"])
        button_group.addButton(self.widgets["home"])

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
        self.widgets["load"].setEnabled(True)  # Enable first step (loading)
        self.widgets["home"].toggle()

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


class AnalysisStepsWidget(QWidget):
    # Stacked widgets for the different steps of the analysis
    # Also includes Welcome page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make iniital widgets
        # Will use same names as AnalysisToolbar so easy to link buttons to corresponding pages:
        # "home", "load", "preprocess", "select", "motorunits", "fibres", "jitter","export"
        self.widgets = {
            "home": WelcomeWidget(parent=self),
            "load": LoadWidget(parent=self),
        }

        # Add to layout
        self.layout = QStackedLayout()
        for w in self.widgets.values():
            self.layout.addWidget(w)
        self.setLayout(self.layout)

    def show_widget(self, widget_name):
        # Slot for signals for changing displayed widget in stacked layout
        self.layout.setCurrentWidget(self.widgets[widget_name])

    def add_preprocess_widget(self):
        # Add preprocessing widget
        # maybe should be method on main window?
        # TODO: check if widget exists before adding?

        print("add preprocessing widget")
        # "preprocess": PreprocWidget(raw_emg_model, settings_model, emg_clrs)
        # connect to toolbar button


# --- Main window ---


class MicroEMGMain(QMainWindow):
    # Main window for microEMG GUI

    def __init__(self):
        super().__init__()

        # Make widgets and toolbars
        self.widgets = {
            "analysistoolbar": AnalysisToolbar("Analysis toolbar"),
            "toptoolbar": TopToolbar(parent=self),
            "analysis": AnalysisStepsWidget(parent=self),
        }

        # Add analysis toolbar to window
        self.addToolBar(Qt.LeftToolBarArea, self.widgets["analysistoolbar"])

        # Add top toolbar and widgets
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widgets["toptoolbar"])  # Add top toolbar
        layout.addWidget(self.widgets["analysis"])  # Add stacked widgets for analysis
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # Connections between analysis toolbar buttons and stacked analysis widgets
        for w_name, w in self.widgets["analysis"].widgets.items():
            self.widgets["analysistoolbar"].widgets[w_name].clicked.connect(
                lambda checked=None, w_name=w_name: self.widgets[
                    "analysis"
                ].show_widget(w_name)
            )

        # Add widget to center
        self.setCentralWidget(widget)

        # Window properties
        self.resize(1200, 800)
