"""
General widget classes to use across GUI.
Modify behaviour of main Qt widget classes.
"""
import microemggui.widget_helpers as meg_help

from PySide6.QtWidgets import (
    QRadioButton,
    QComboBox,
    QLabel,
    QSpinBox,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
)

from PySide6.QtCore import Qt


class RadioButtonMain(QRadioButton):
    # Radio button, main text (start of section)
    # Class used to set spacing and styling of this widget across GUI
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        meg_help.fix_widget_size(self, w, h)


class InputLabel(QLabel):
    # Label for input field (e.g., combobox)
    # Class used to set spacing and styling of this widget across GUI
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        meg_help.fix_widget_size(self, w, h)

        # Alignment
        self.setAlignment(Qt.AlignBottom)


class InlineLabel(QLabel):
    # Label for text that is inline with other widgets
    # TODO: add styling input and apply styling
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)


class InputComboBox(QComboBox):
    # Combobox with fixed size
    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        meg_help.fix_widget_size(self, w, h)


class InputSpinBox(QSpinBox):
    # Spinbox with fixed size

    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        meg_help.fix_widget_size(self, w, h)


class InputLineEdit(QLineEdit):
    # LineEdit with fixed size

    def __init__(self, *args, w=None, h=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Fix size to specified width and height
        meg_help.fix_widget_size(self, w, h)


class ExpandingSpacer(QSpacerItem):
    # Spacer with minimum size of (0, 0) that will expand to fill available space in
    # widget.
    # Used to keep other widgets a fixed size.
    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
