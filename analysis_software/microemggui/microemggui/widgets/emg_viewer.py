"""
Widget for viewing EMG time series.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout

from microemggui.widgets.base import (
    InputInlineLabel,
    # InputWarningLabel,
    # InputComboBox,
    InputLineEdit,
    InputInlineText,
    # ExpandingSpacer,
)

# --- Widgets for controlling time window ---


class StartTimeWidget(QWidget):
    # Widget for specifying start time of window for viewing EMG data

    # TODO: add validation and warning for time based on size of EMG data

    def __init__(self, parent=None):
        super().__init__(parent)

        # Inline label
        self.widgets = {
            "start_label": InputInlineLabel("Start: ", self),
            "time_lineedit": InputLineEdit(self),
            "s_label": InputInlineText("seconds", self),
        }

        # Add widgets to horizontal layout
        layout = QHBoxLayout()
        for _, w in self.widgets.items():
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
