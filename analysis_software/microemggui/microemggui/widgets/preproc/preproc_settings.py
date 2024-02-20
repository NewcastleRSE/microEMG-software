"""
Widgets for specifying preprocessing settings
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

        # Horizontal layout for frequency input
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


class FilterSpecWidget(QWidget):
    # Widget for all filter specifications
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Widgets for filter specifications
        self.filter_spec_widgets = [
            FilterTypeWidget(self),  # type
            FilterFreqWidget(self),  # frequencies
            FilterOrderWidget(self),  # order
        ]

        # Add to filter specifications to vertical layout
        layout = QVBoxLayout()
        for w in self.filter_spec_widgets:
            layout.addWidget(w)
        layout.setContentsMargins(50, 0, 0, 0)  # add padding to left
        self.setLayout(layout)


class PreprocSettingsWidget(QWidget):
    # Widget for all preprocessing settings
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Radio button for selecting mains noise removal
        mains_radio = RadioButtonMain("Remove mains noise (50 Hz)", self)

        # Radio button for selecting filter
        filter_radio = RadioButtonMain("Filter", self)

        # Filter settings
        filter_settings = FilterSpecWidget(self)

        # All widgets
        self.preproc_widgets = [mains_radio, filter_radio, filter_settings]

        # Create layout and add widgets
        layout = QVBoxLayout()
        for w in self.preproc_widgets:
            layout.addWidget(w)
        layout.setContentsMargins(0, 0, 0, 0)

        # Spacer at end so extra space is added below other widgets if window resized
        end_space = ExpandingSpacer()
        layout.addItem(end_space)

        self.setLayout(layout)
