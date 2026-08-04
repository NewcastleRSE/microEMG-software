"""Shared pytest fixtures for the microemggui test suite."""

import os

import pytest

from pymicroemg.demo_data import demo_data_exists, download_and_extract_demo


# Never trigger the launch-time demo-data prompt while tests are running.
os.environ.setdefault("MICROEMG_DISABLE_DEMO_PROMPT", "1")


@pytest.fixture(scope="session")
def ensure_demo_data():
    """Ensure the demo recording is present before running demo-dependent tests.

    Tests that need the recording should depend on this fixture (either directly
    or transitively via their data fixtures). Set ``MICROEMG_SKIP_DEMO_DOWNLOAD=1``
    to skip such tests instead of triggering a ~1 GB download.
    """
    if demo_data_exists():
        return
    if os.environ.get("MICROEMG_SKIP_DEMO_DOWNLOAD") == "1":
        pytest.skip(
            "demo recording not present; unset MICROEMG_SKIP_DEMO_DOWNLOAD to auto-download"
        )
    download_and_extract_demo()
