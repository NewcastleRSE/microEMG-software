#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget for home page. Includes information about the GUI (e.g., license, attributions)
"""

from typing import Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from microemggui.widgets.base import (
    SectionTitle,
    ExpandingVSpacer,
)


# --- Home page widget ---


class HomeWidget(QWidget):
    """
    Widget for home (welcome) page.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create widgets
        self.widgets: dict[str, Any] = {
            "title": SectionTitle("Welcome to the microEMG analysis GUI", parent=self)
        }

        # Add to layout
        layout = QVBoxLayout()
        for w in self.widgets.values():
            layout.addWidget(w)
        layout.addItem(ExpandingVSpacer())  # spacer
        layout.setContentsMargins(20, 5, 20, 20)
        self.setLayout(layout)
