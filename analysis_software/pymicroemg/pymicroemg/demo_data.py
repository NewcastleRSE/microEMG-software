"""On-demand download and extraction of the demo EMG recording.

The demo recording is no longer bundled in the repository. Callers that want
it (the GUI, `data_analysis/example_pipeline.py`, tests) can query
`demo_data_exists()` and, if False, call `download_and_extract_demo()` to
fetch it from the project's GitHub release.
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
import sys
import tarfile
import tempfile
import threading
import urllib.request
from importlib.resources import as_file, files
from pathlib import Path
from typing import Callable, Optional

from platformdirs import user_data_dir


DEMO_URL = (
    "https://github.com/NewcastleRSE/microEMG-software/releases/download/demo-data-v1/demo-data.tar"
)

# Marker file used to detect a successfully-extracted demo directory.
_MARKER = "info.rhd"

# Streaming download tuning.
_CHUNK_SIZE = 1024 * 1024  # 1 MiB
_PROGRESS_STRIDE = 4 * _CHUNK_SIZE  # emit progress at most every 4 MiB
_SOCKET_TIMEOUT = 30  # seconds

logger = logging.getLogger("pymicroemg.demo_data")


class DemoDataMissingError(FileNotFoundError):
    """Raised when the demo recording is expected but has not been downloaded."""


class DemoDownloadCancelled(Exception):
    """Raised inside download_and_extract_demo when the cancel event is set."""


def _user_data_dir() -> Path:
    return Path(user_data_dir("microEMG", "NewcastleRSE")) / "recordings" / "64-channel"


def _packaged_dir() -> Optional[Path]:
    """Return the packaged '64-channel' directory if one is discoverable, else None."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidate = Path(sys._MEIPASS) / "pymicroemg" / "data" / "recordings" / "64-channel"
        return candidate
    try:
        pkg_path = files("pymicroemg").joinpath("data", "recordings", "64-channel")
        with as_file(pkg_path) as p:
            return Path(os.fspath(p))
    except (ModuleNotFoundError, FileNotFoundError):
        return None


def _has_demo(base: Optional[Path]) -> bool:
    if base is None:
        return False
    marker = base / "demo1" / _MARKER
    try:
        return marker.is_file() and marker.stat().st_size > 0
    except OSError:
        return False


def get_demo_data_dir() -> Path:
    """Return the directory that contains (or will contain) the ``demo1/`` folder.

    Search order:
        1. The user data dir, if it already holds a valid demo.
        2. The packaged path (PyInstaller ``_MEIPASS`` or installed package resources),
           if it already holds a valid demo. This supports legacy installs where the
           demo was bundled.
        3. The user data dir, returned as the intended download target.

    This function never raises for a missing demo; callers should use
    :func:`demo_data_exists` to distinguish present-vs-absent.
    """
    user_dir = _user_data_dir()
    if _has_demo(user_dir):
        return user_dir
    packaged = _packaged_dir()
    if _has_demo(packaged):
        return packaged  # type: ignore[return-value]
    return user_dir


def demo_data_exists() -> bool:
    """True iff the demo1 recording is present and non-empty at the resolved location."""
    return _has_demo(get_demo_data_dir())


def _emit(progress_cb: Optional[Callable[[int, int], None]], read: int, total: int) -> None:
    if progress_cb is not None:
        try:
            progress_cb(read, total)
        except Exception:
            logger.exception("progress callback raised; continuing download")


def download_and_extract_demo(
    progress_cb: Optional[Callable[[int, int], None]] = None,
    cancel_event: Optional[threading.Event] = None,
) -> Path:
    """Download the demo tarball and extract it to ``get_demo_data_dir() / 'demo1'``.

    Parameters
    ----------
    progress_cb : callable, optional
        Called as ``progress_cb(bytes_read, total_bytes)`` during download.
        Throttled to at most every 4 MiB. ``total_bytes`` is 0 if the server does
        not send Content-Length.
    cancel_event : threading.Event, optional
        Checked between chunks; if set, raises :class:`DemoDownloadCancelled` and
        cleans up any partial artefacts.

    Returns
    -------
    Path
        The extracted ``demo1/`` directory.
    """
    target_parent = get_demo_data_dir()
    target_parent.mkdir(parents=True, exist_ok=True)
    final_dir = target_parent / "demo1"
    partial_dir = target_parent / ".demo1.partial"

    if partial_dir.exists():
        shutil.rmtree(partial_dir, ignore_errors=True)

    tmp = tempfile.NamedTemporaryFile(
        dir=str(target_parent), prefix=".demo-data.", suffix=".tar", delete=False
    )
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        logger.info("Downloading demo data from %s", DEMO_URL)
        with urllib.request.urlopen(DEMO_URL, timeout=_SOCKET_TIMEOUT) as resp:
            total = int(resp.headers.get("Content-Length") or 0)
            read = 0
            last_emit = 0
            hasher = hashlib.sha256()
            with open(tmp_path, "wb") as f:
                _emit(progress_cb, 0, total)
                while True:
                    if cancel_event is not None and cancel_event.is_set():
                        raise DemoDownloadCancelled()
                    chunk = resp.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    hasher.update(chunk)
                    read += len(chunk)
                    if read - last_emit >= _PROGRESS_STRIDE:
                        _emit(progress_cb, read, total)
                        last_emit = read
            _emit(progress_cb, read, total)

        if total and read != total:
            raise IOError(
                f"Download truncated: got {read} bytes, expected {total} (Content-Length)."
            )
        logger.info("Downloaded %d bytes (sha256=%s)", read, hasher.hexdigest())

        logger.info("Extracting demo data to %s", final_dir)
        partial_dir.mkdir(parents=True, exist_ok=False)
        with tarfile.open(tmp_path, mode="r:*") as tar:
            try:
                tar.extractall(partial_dir, filter="data")
            except TypeError:
                # Python < 3.12 has no ``filter`` kwarg.
                tar.extractall(partial_dir)

        if final_dir.exists():
            shutil.rmtree(final_dir)
        os.replace(partial_dir, final_dir)
        logger.info("Demo data ready at %s", final_dir)
        return final_dir

    except BaseException:
        # Clean up any partial extraction on any failure (including KeyboardInterrupt).
        if partial_dir.exists():
            shutil.rmtree(partial_dir, ignore_errors=True)
        raise
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Failed to delete temp file %s", tmp_path)
