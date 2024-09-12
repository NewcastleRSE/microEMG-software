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
    QPushButton,
    QToolButton,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import QSize

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT


# --- Settings input ---


class CheckBoxMain(QCheckBox):
    """
    Checkbox that also marks the start of a settings section.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CheckBoxChannel(QCheckBox):
    """
    Checkbox for selecting EMG channel.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CheckBoxRegular(QCheckBox):
    """
    Checkbox that is not emphasised (not a section heading)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputComboBox(QComboBox):
    """
    Combobox for settings input.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputSpinBox(QSpinBox):
    """
    Spinbox for settings input.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputLineEdit(QLineEdit):
    """
    Line edit (text field) for settings input.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Labels ---
# Note that "input" labels/text are also used more generally for messages that are not
# associated with specified inputs.


class InputLabel(QLabel):
    """
    Label for settings input field (e.g., combobox) that goes above the input widget.
    Has emphasised text.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineLabel(QLabel):
    """
    Inline label for settings input field that is inline with the input widget.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineText(QLabel):
    """
    Text that is inline with another widget, but is not label for widget (e.g., units).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineHighlightedText(QLabel):
    """
    Text that is inline with other widget, but not label for widget (e.g., units).
    Highlighted in the accent colour in the style sheet to make more prominent.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputWarningLabel(QLabel):
    """
    Label for warning/error text for input fields or other GUI messages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class InputExplanationLabel(QLabel):
    """
    Explanation text for settings input.
    Lighter text colour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)


class SubsectionTitle(QLabel):
    """
    Label for subsection of a larger widget (e.g., settings).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SectionTitle(QLabel):
    """
    Label for a page (widget) in the GUI (e.g., preprocessing step).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisToolbarLabel(QLabel):
    """
    Labels for sections in analysis toolbar.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HighlightedLabel(QLabel):
    """
    Label highlighted in a different colour to make more prominent.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class ResultsLabel(QLabel):
    """
    Label for displaying results (e.g., summary statistics)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MessageLabel(QLabel):
    """
    Label for GUI message without prominent text.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class TitleInputLabel(QLabel):
    """
    Label for an input field that also serves as a title.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Buttons ---


class SmallPushButton(QPushButton):
    """
    Small push buttons (i.e., secondary buttons).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LargePushButton(QPushButton):
    """
    Large push buttons (i.e., primary buttons).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisToolbarButton(QPushButton):
    """
    Push buttons for the analysis toolbar.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WidgetControlButton(QToolButton):
    """
    Small tool buttons for controlling a widget (e.g., the EMG viewer plot settings).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MotorUnitButton(QPushButton):
    """
    Button for motor units in the select motor units (selectmu) widget.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Spacers ---


class ExpandingSpacer(QSpacerItem):
    """
    Spacer with minimum size of (0, 0) that will expand to fill available space in
    widget.
    Used to keep other widgets a fixed size.
    """

    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)


class ExpandingVSpacer(QSpacerItem):
    """
    Spacer with minimum size of (0, 0) that will expand vertically to fill available
    space in widget.
    Used to keep other widgets a fixed size.
    """

    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)


class ExpandingHSpacer(QSpacerItem):
    """
    Spacer with minimum size of (0, 0) that will expand horizontally to fill available
    space in widget.
    Used to keep other widgets a fixed size.
    """

    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)


# --- Misc widgets ---


class MatplotlibToolbar(NavigationToolbar2QT):
    """
    Toolbar for controlling/saving matplotlib plots.
    This child class decreases the size of the icons.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(20, 20))
