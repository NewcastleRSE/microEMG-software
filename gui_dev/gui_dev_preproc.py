#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:10:56 2024

@author: Gabrielle
"""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QRadioButton,
    QComboBox,
    QLabel,
    QSpinBox,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
)

# FUNCTIONS


def fix_widget_size(my_widget, w, h):
    # Set widget min size and set size policy to Fixed

    # set size properties
    w_sz = my_widget.sizeHint()
    if w is not None:
        w_sz.setWidth(w)
    if h is not None:
        w_sz.setHeight(h)
    my_widget.setMinimumSize(w_sz)
    my_widget.setMaximumSize(w_sz)

    # size policy = fixed so does not expand if widget size changes
    my_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


# FORMATTING CLASSES


# Spacing settings to pass to GUI
class SpacingSettings:
    def __init__(self, h_major, h_minor):
        self.h_major = h_major
        self.h_minor = h_minor


# GENERAL CLASSES


class RadioButtonMain(QRadioButton):
    # Radio button, main text
    # Class used to set spacing and styling of this widget across GUI
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        fix_widget_size(self, w, h)


class InputLabel(QLabel):
    # Label for input field (e.g., combobox)
    # Class used to set spacing and styling of this widget across GUI
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        fix_widget_size(self, w, h)


class ComboBoxSmall(QComboBox):
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        fix_widget_size(self, w, h)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


class ExpandingSpacer(QSpacerItem):
    # Spacer with minimum size of (0, 0) that will expand to fill available space in
    # widget.
    # Used to keep other widgets a fixed size.
    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)


# Filter settings classes


class FilterSettingsWidget(QWidget):
    def __init__(self, spacing_settings):
        super().__init__()

        # set up layout
        layout = QGridLayout()
        row_idx = 0
        col_idx = 0

        row_span = 1
        col_span = 4

        # add radio for specifying whether to filter
        self.filter_radio = RadioButtonMain("Filter", self, h=spacing_settings.h_major)
        layout.addWidget(self.filter_radio, row_idx, col_idx, row_span, col_span)

        # Vertical layout for filter type, frequencies, and order
        layout_spec = QVBoxLayout()

        # input for filter type from combobox (dropdown), with label above
        self.type_label = InputLabel("Type", self, h=spacing_settings.h_minor)
        self.type_combobox = ComboBoxSmall(self, w=100, h=spacing_settings.h_minor)
        filter_types = ["Lowpass", "Highpass", "Bandpass"]
        self.type_combobox.addItems(filter_types)
        layout_spec.addWidget(self.type_label)
        layout_spec.addWidget(self.type_combobox)

        # input for cutoff frequencies
        # input will be provided in horizontal layout
        # TODO: add validator (QDoubleValidator?)
        self.freq_label = InputLabel(
            "Cutoff frequencies", self, h=spacing_settings.h_minor
        )
        layout_freq = QHBoxLayout()
        self.freq_widgets = [
            QLineEdit(self),
            QLabel("to", self),
            QLineEdit(self),
            QLabel("Hz", self),
        ]
        for w in self.freq_widgets:
            layout_freq.addWidget(w)
        layout_freq.setContentsMargins(0, 0, 0, 0)
        self.freq_widget = QWidget()
        self.freq_widget.setLayout(layout_freq)

        # add to main layout
        layout_spec.addWidget(self.freq_label)
        layout_spec.addWidget(self.freq_widget)

        # Input for filter order
        self.order_label = InputLabel("Order", self, h=spacing_settings.h_minor)
        self.order_spinbox = QSpinBox(self)
        self.order_spinbox.setRange(2, 8)
        self.order_spinbox.setSingleStep(2)
        self.order_spinbox.lineEdit().setReadOnly(True)
        layout_spec.addWidget(self.order_label)
        layout_spec.addWidget(self.order_spinbox)

        self.filter_spec_widget = QWidget()
        self.filter_spec_widget.setLayout(layout_spec)

        # Add to grid layout

        # horizontal offset for widgets specifying filter settings
        col_idx += col_span - 2
        row_idx += 1
        layout.addWidget(self.filter_spec_widget, row_idx, col_idx, row_span, col_span)

        # Spacer at end so extra space is added below other widgets if window resized
        self.end_space = ExpandingSpacer()
        row_idx += 1
        layout.addItem(self.end_space, row_idx, 0)

        # set layout
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, spacing_settings):
        super().__init__()

        self.filter_settings_widget = FilterSettingsWidget(spacing_settings)

        self.setCentralWidget(self.filter_settings_widget)


spacing_settings = SpacingSettings(h_major=50, h_minor=20)

app = QApplication(sys.argv)
window = MainWindow(spacing_settings=spacing_settings)
window.show()

app.exec()
