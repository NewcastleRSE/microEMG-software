"""
Widgets for specifying filter settings during preprocessing step
"""
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from microemggui.widgets.base import (
    RadioButtonMain,
    InputLabel,
    InputComboBox,
    InputSpinBox,
    InputLineEdit,
    InputInlineLabel,
    ExpandingSpacer,
)


class FilterTypeWidget(QWidget):
    # Widget for specifying filter type from labelled combobox
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Label for filter type
        self.type_label = InputLabel("Type", self)

        # Input for filter type
        self.type_combobox = InputComboBox(self)

        filter_types = ["Lowpass", "Highpass", "Bandpass"]
        self.type_combobox.addItems(filter_types)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combobox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FilterOrderWidget(QWidget):
    # Widget for specifying the filter order from a spinbox
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Label
        self.order_label = InputLabel("Order", self)

        # Spinbox with range from 2 to 8, in steps of 2
        self.order_spinbox = InputSpinBox(self)
        self.order_spinbox.setRange(2, 8)
        self.order_spinbox.setSingleStep(2)

        # Set to ready only so cannot edit to odd number
        self.order_spinbox.lineEdit().setReadOnly(True)

        # Add to layout
        layout = QVBoxLayout()
        layout.addWidget(self.order_label)
        layout.addWidget(self.order_spinbox)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FilterFreqWidget(QWidget):
    # Widget for specifying the filter frequencies from input boxes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: add input validator (QDoubleValidator?)

        # Label
        self.freq_label = InputLabel("Cutoff frequencies", self)

        # Widgets for specifying frequencies
        self.freq_input_widgets = [
            InputLineEdit(self),
            InputInlineLabel("to", self),
            InputLineEdit(self),
            InputInlineLabel("Hz", self),
        ]

        # Horitzontal layout for frequency input
        layout_input = QHBoxLayout()
        for w in self.freq_input_widgets:
            layout_input.addWidget(w)
        layout_input.setContentsMargins(0, 0, 0, 0)
        self.freq_input = QWidget(self)
        self.freq_input.setLayout(layout_input)

        # Add label and input to overall layout
        layout = QVBoxLayout()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_input)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class FilterSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up layout for entire widget
        layout = QVBoxLayout()

        # Add radio for specifying whether to filter
        self.filter_radio = RadioButtonMain("Filter", self)
        layout.addWidget(self.filter_radio)

        # Widgets for filter specifications
        self.filter_spec_widgets = [
            FilterTypeWidget(self),  # type
            FilterFreqWidget(self),  # frequencies
            FilterOrderWidget(self),  # order
        ]

        # Add to filter specifications to vertical layout
        layout_spec = QVBoxLayout()
        for w in self.filter_spec_widgets:
            layout_spec.addWidget(w)
        layout_spec.setContentsMargins(50, 0, 0, 0)  # add padding to left
        self.filter_spec = QWidget(self)
        self.filter_spec.setLayout(layout_spec)

        # Add filter specifications to overall layout
        layout.addWidget(self.filter_spec)

        # Spacer at end so extra space is added below other widgets if window resized
        self.end_space = ExpandingSpacer()
        layout.addItem(self.end_space)

        # set layout
        self.setLayout(layout)
