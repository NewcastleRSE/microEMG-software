#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes for passing logger records to GUI.

Based on https://docs.python.org/3/howto/logging-cookbook.html
"""

import logging
from PySide6.QtCore import Signal, QObject


class LogRecordSignaller(QObject):
    # QObject for passing log record signal

    signal = Signal(logging.LogRecord)


class QtHandler(logging.Handler):
    # Logger handler for passing analysis info to GUI.

    def __init__(self, slot_func, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create QObject for emitting signal
        self.signaller = LogRecordSignaller()

        # Connect to slot
        self.signaller.signal.connect(slot_func)

    def emit(self, record):
        # Emit log record
        self.signaller.signal.emit(record)
