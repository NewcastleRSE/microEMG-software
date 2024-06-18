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


class CheckBoxMain(QCheckBox):
    # Radio button, main text (start of settings section)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Settings input ---


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


# --- Labels ---
# TODO: consider changing input text labels to more generic names (usable for more than input)


class InputLabel(QLabel):
    # Label for input field (e.g., combobox)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineLabel(QLabel):
    # Inline label for input field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineText(QLabel):
    # Text that is inline with other widget, but not label for widget (e.g., units)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputInlineHighlightedText(QLabel):
    # Text that is inline with other widget, but not label for widget (e.g., units)
    # Highlighted in a different colour to make more prominent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InputWarningLabel(QLabel):
    # Label for warning/error text for input fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWordWrap(True)


class SubsectionTitle(QLabel):
    # Label for subsection of a larger widget (e.g., settings)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SectionTitle(QLabel):
    # Label for a larger widget (e.g., preprocessing step)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisToolbarLabel(QLabel):
    # Labels for sections in analysis toolbar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Buttons ---


class SmallPushButton(QPushButton):
    # Small push buttons
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LargePushButton(QPushButton):
    # Large push buttons
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisToolbarButton(QPushButton):
    # Push buttons for analysis toolbar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WidgetControlButton(QToolButton):
    # Button for controlling widget (e.g., EMG viewer plot settings)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TabButton(QPushButton):
    # "Button" for tabs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# --- Spacers ---


class ExpandingSpacer(QSpacerItem):
    # Spacer with minimum size of (0, 0) that will expand to fill available space in
    # widget.
    # Used to keep other widgets a fixed size.
    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)


class ExpandingVSpacer(QSpacerItem):
    # Spacer with minimum size of (0, 0) that will expand vertically to fill available
    # space in widget.
    # Used to keep other widgets a fixed size.
    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)


class ExpandingHSpacer(QSpacerItem):
    # Spacer with minimum size of (0, 0) that will expand horizontally to fill available
    # space in widget.
    # Used to keep other widgets a fixed size.
    def __init__(self):
        super().__init__(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
