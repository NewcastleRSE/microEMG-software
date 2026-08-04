"""Launch-time prompt and background worker for downloading the demo recording."""

from __future__ import annotations

import logging
import os
import threading

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import QDialog, QMessageBox, QProgressDialog, QWidget

from pymicroemg.demo_data import (
    DemoDownloadCancelled,
    demo_data_exists,
    download_and_extract_demo,
)


logger = logging.getLogger("microemggui.demo_data")


class DownloadWorker(QThread):
    """Runs :func:`download_and_extract_demo` on a background thread."""

    progress = Signal(int, int)  # bytes_read, total_bytes
    finished_ok = Signal()
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancel = threading.Event()

    def cancel(self) -> None:
        self._cancel.set()

    def _on_progress(self, read: int, total: int) -> None:
        # Emitted from this worker thread; Qt marshals to the receiver's thread.
        self.progress.emit(read, total)

    def run(self) -> None:  # noqa: D401
        try:
            download_and_extract_demo(
                progress_cb=self._on_progress,
                cancel_event=self._cancel,
            )
        except DemoDownloadCancelled:
            self.cancelled.emit()
        except Exception as exc:
            logger.exception("Demo data download failed")
            self.failed.emit(str(exc))
        else:
            self.finished_ok.emit()


def prompt_and_maybe_download(parent: QWidget) -> bool:
    """Prompt the user; if they accept, download the demo. Return True iff demo now exists.

    Behaviour:
      * No-op and return True if the demo is already present.
      * Silent no-op returning False if ``MICROEMG_DISABLE_DEMO_PROMPT=1`` in the env
        (used by tests and CI so constructing the main window doesn't trigger UI).
      * Otherwise show a Yes/No message box. On No, return False.
      * On Yes, show a modal progress dialog while a background thread downloads and
        extracts. Cancelable. Returns True on success, False otherwise.
    """
    if demo_data_exists():
        return True

    if os.environ.get("MICROEMG_DISABLE_DEMO_PROMPT") == "1":
        logger.info("Demo prompt suppressed by MICROEMG_DISABLE_DEMO_PROMPT=1")
        return False

    reply = QMessageBox.question(
        parent,
        "Demo data",
        "Demo data is not available. Download this now? (~1 GB)",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes,
    )
    if reply != QMessageBox.Yes:
        logger.info("User declined to download demo data.")
        return False

    dialog = QProgressDialog("Downloading demo data...", "Cancel", 0, 100, parent)
    dialog.setWindowTitle("Demo data")
    dialog.setWindowModality(Qt.WindowModal)
    dialog.setMinimumDuration(0)
    dialog.setAutoClose(False)
    dialog.setAutoReset(False)
    dialog.setValue(0)

    worker = DownloadWorker(parent)
    failure = {"msg": ""}

    def _on_progress(read: int, total: int) -> None:
        if total > 0:
            dialog.setMaximum(100)
            dialog.setValue(int(read * 100 / total))
            dialog.setLabelText(
                f"Downloading demo data... {read / 1e6:.0f} / {total / 1e6:.0f} MB"
            )
        else:
            dialog.setMaximum(0)
            dialog.setLabelText(f"Downloading demo data... {read / 1e6:.0f} MB")

    def _on_failed(msg: str) -> None:
        failure["msg"] = msg
        dialog.reject()

    # Use the dialog's own modal exec() as our event loop; worker outcomes
    # map to dialog.accept()/reject(). Qt.QueuedConnection guarantees the
    # slots run on the main (dialog's) thread even when emitted from the
    # worker thread — this is what avoids the hang.
    worker.progress.connect(_on_progress, Qt.QueuedConnection)
    worker.finished_ok.connect(dialog.accept, Qt.QueuedConnection)
    worker.cancelled.connect(dialog.reject, Qt.QueuedConnection)
    worker.failed.connect(_on_failed, Qt.QueuedConnection)
    dialog.canceled.connect(worker.cancel)

    worker.start()
    result_code = dialog.exec()
    worker.wait()

    if failure["msg"]:
        QMessageBox.warning(parent, "Demo data", f"Download failed:\n\n{failure['msg']}")

    return result_code == QDialog.Accepted
