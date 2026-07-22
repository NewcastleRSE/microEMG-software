#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for defining style settings (e.g., colours) and getting style sheet.
"""

import os
import sys
from PySide6.QtCore import QFile
import microemggui


def get_gui_style_sheet() -> str:
    """
    Load GUI style sheet as string.

    Returns
    -------
    str
        GUI style sheet.

    """

    # Get path to style sheet
    # When running under PyInstaller, files are in sys._MEIPASS; otherwise use module path
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as PyInstaller bundle
        style_path = os.path.join(sys._MEIPASS, "microemggui", "styles", "style.qss")
    else:
        # Running as normal Python module
        style_dir = microemggui.__file__
        style_dir = style_dir[:-11]  # remove __init__.py
        style_path = os.path.join(style_dir, "styles", "style.qss")

    # Load style sheet
    gui_style_file = QFile(style_path)
    gui_style_file.open(QFile.OpenModeFlag.ReadOnly)
    gui_style_sheet = gui_style_file.readAll().toStdString()

    return gui_style_sheet


def get_formatted_gui_style_sheet(clr="teal") -> str:
    """
    Get and format style sheet (replaces variables defined in style sheet with
    corresponding values).

    Also defines values for variables in the style sheet.

    Parameters
    ----------
    clr : TYPE, optional
        String to specify primary colour (e.g., used for buttons). The default is
        "teal".

    Returns
    -------
    str
        Formatted style sheet.

    """

    # Get style sheet
    gui_style_sheet = get_gui_style_sheet()

    # Dictionary of terms to replace (all marked with {} ) in style sheet
    # Note on MacOS, background by default is #ececec -
    # colours should have good contrast with that colour.

    # Primary colour, with variations for different states

    match clr:
        case "teal":
            # teal
            clr_primary = "#30819C"
            clr_primary_disabled = "#A4C1CB"
            clr_primary_hover = "#276A7E"
            clr_primary_pressed = "#1E5362"
            clr_primary_dark = "#276A7E"
        case "gold":
            # golden brown
            clr_primary = "#A77E28"
            clr_primary_disabled = "#D1BF8A"
            clr_primary_hover = "#8B671F"
            clr_primary_pressed = "#705019"
            clr_primary_dark = "#8C671E"
        case _:
            raise ValueError("Requested primary colour (clr) is not an option.")

    # Other colors to consider:
    # dark purple: #4B0082
    # purple: #6A1B9A
    # forest green: #228B22
    # green: #39B54A
    # deep navy blue: #004080
    # purple blue: 6A5ACD
    # more vibrant teal: "#1C7DA6"

    # Secondary colour (will set to same colour as primary, but use separate
    # variable for flexibility)
    clr_secondary = clr_primary

    # Dictionary for defining different variables in style sheet
    style_var = {
        # theme colors
        "{clr_primary}": clr_primary,  # should have high contrast with white
        "{clr_primary_dark}": clr_primary_dark,  # darker version for text on light background
        "{clr_primary_disabled}": clr_primary_disabled,
        "{clr_primary_hover}": clr_primary_hover,
        "{clr_primary_pressed}": clr_primary_pressed,
        "{clr_secondary}": clr_secondary,
        "{clr_warning}": "#A33221",  # should be a shade of red/orange
        # text colors
        "{clr_text_dark}": "#0D0D0D",
        "{clr_text_medium}": "#404040",
        "{clr_text_light}": "#656565",
        "{clr_text_very_light}": "#949494",
        # large buttons - will use primary colors directly
        "{clr_large_button_text}": "white",  # light text
        # small buttons - will use primary colors directly as outline and text
        "{clr_small_button}": "white",
        # icon buttons
        "{clr_control_button}": "#f2f2f2",
        "{clr_control_button_hover}": "#d9d9d9",
        "{clr_control_button_pressed}": "#cccccc",
        "{clr_control_button_disabled}": "#a6a6a6",
        # all buttons
        "{radius_button}": "4",
        # borders
        "{clr_border}": "#808080",
        "{clr_border_light}": "#D9D9D9",
        # background color (for when do not use default)
        "{clr_background}": "white",
    }

    # Replace variables in style sheet with corresponding values
    for k, v in style_var.items():
        gui_style_sheet = gui_style_sheet.replace(k, v)

    # Return formatted style sheet
    return gui_style_sheet
