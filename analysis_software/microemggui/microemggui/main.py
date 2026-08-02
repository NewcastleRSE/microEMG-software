#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load and execute full microEMG GUI
"""

import sys

from PySide6.QtWidgets import QApplication

from microemggui.widgets.main.main_window import MicroEMGMain
from microemggui.styles.gui_style import get_formatted_gui_style_sheet
from microemggui.gui_logger import set_up_gui_logging


def main() -> None:
    """Launch the microEMG GUI application."""
    set_up_gui_logging()

    app = QApplication(sys.argv)
    window = MicroEMGMain()
    window.show()

    # Apply style (clr options are "teal" (default) or "gold")
    gui_style_sheet = get_formatted_gui_style_sheet(clr="teal")
    app.setStyleSheet(gui_style_sheet)

    app.exec()


if __name__ == "__main__":
    main()
