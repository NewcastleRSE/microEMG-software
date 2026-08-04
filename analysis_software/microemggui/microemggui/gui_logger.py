#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes for passing logger records to GUI.

Function for setting up logging.

Based on https://docs.python.org/3/howto/logging-cookbook.html
"""

import logging
import logging.handlers
import pathlib

import platformdirs
from PySide6.QtCore import Signal, QObject
from pymicroemg.emg_data_raw import EMGDataRawLoggerAdapter

# --- Classes for loggers used to provide info to progress bars ---


class LogRecordSignaller(QObject):
    """
    QObject for passing log record signal.
    """

    signal = Signal(EMGDataRawLoggerAdapter)


class QtHandler(logging.Handler):
    """
    Logger handler for passing analysis info to GUI.
    """

    def __init__(self, slot_func, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create QObject for emitting signal
        self.signaller = LogRecordSignaller()

        # Connect to slot
        self.signaller.signal.connect(slot_func)

    def emit(self, record: EMGDataRawLoggerAdapter):
        # Emit log record
        self.signaller.signal.emit(record)


# --- Function for set up for logger for entire GUI ---


def set_up_gui_logging():
    """
    Set up logging for GUI. Includes console output at INFO level and rotating file
    logging at INFO level.

    Log file is written to the OS user log directory and rotated automatically
    (max 250 KB per file, 10 backups kept).
    """
    # Handler for console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Handler for file — write to user log dir so it works regardless of CWD
    log_dir = pathlib.Path(platformdirs.user_log_dir("microEMG", "NewcastleRSE"))
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.handlers.RotatingFileHandler(
        log_dir / "microemggui.log",
        maxBytes=250_000,
        backupCount=10,
    )
    fh.setLevel(logging.INFO)

    # format
    logger_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(logger_formatter)
    fh.setFormatter(logger_formatter)

    # add handlers
    logging.getLogger().addHandler(ch)
    logging.getLogger().addHandler(fh)

    # Change level of root logger
    logging.getLogger().setLevel(logging.INFO)
