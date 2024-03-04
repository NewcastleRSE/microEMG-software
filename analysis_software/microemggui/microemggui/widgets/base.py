"""
General widget classes to use across GUI.
Either modify behaviour of main Qt widget classes or are used to refer to specific
groups of widgets in the style sheet.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QSpinBox,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
)


class CheckBoxMain(QCheckBox):
    # Radio button, main text (start of settings section)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Settings input ---


class InputLabel(QLabel):
    # Label for input field (e.g., combobox)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineLabel(QLabel):
    # Label for text that is inline with other widgets
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputWarningLabel(QLabel):
    # Label for warning/error text for input fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputComboBox(QComboBox):
    # Combobox for settings input
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputSpinBox(QSpinBox):
    # Spinbox for settings input
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputLineEdit(QLineEdit):
    # LineEdit for settings input
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Spacers ---


class ExpandingSpacer(QSpacerItem):
    # Spacer with minimum size of (0, 0) that will expand to fill available space in
    # widget.
    # Used to keep other widgets a fixed size.
    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
