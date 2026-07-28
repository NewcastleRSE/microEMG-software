"""Tests for the export step widget's default directory logic."""

import os
from unittest.mock import MagicMock, patch

import pytest

from pymicroemg.demo_data import get_demo_data_dir


@pytest.fixture
def export_widget():
    """Create an ExportWidget with a mocked reconstruct model."""
    from microemggui.widgets.export.export_step import ExportWidget

    mock_model = MagicMock()
    recording_path = "/some/user/recording/path"
    widget = ExportWidget(mock_model, recording_path)
    return widget


class TestBrowseDefaultDir:
    """Verify that the file browser defaults to home when using demo data."""

    def test_default_dir_is_recording_path_for_user_data(self, qtbot, export_widget):
        recording_path = export_widget.recording_path

        with patch(
            "microemggui.widgets.export.export_step.QFileDialog.getExistingDirectory",
            return_value="",
        ) as mock_dialog:
            export_widget.browse_for_export_folder()
            call_args = mock_dialog.call_args
            assert call_args[0][2] == recording_path

    def test_default_dir_is_home_for_downloaded_demo_data(self, qtbot):
        from microemggui.widgets.export.export_step import ExportWidget

        demo_dir = str(get_demo_data_dir())
        demo_recording_path = os.path.join(demo_dir, "demo1", "raw")
        mock_model = MagicMock()
        widget = ExportWidget(mock_model, demo_recording_path)

        with patch(
            "microemggui.widgets.export.export_step.QFileDialog.getExistingDirectory",
            return_value="",
        ) as mock_dialog:
            widget.browse_for_export_folder()
            call_args = mock_dialog.call_args
            assert call_args[0][2] == os.path.expanduser("~")

    def test_default_dir_is_home_for_bundled_demo_data(self, qtbot):
        from microemggui.widgets.export.export_step import ExportWidget

        mock_model = MagicMock()
        fake_meipass = "/tmp/fake_meipass"
        recording_path = os.path.join(fake_meipass, "recordings", "demo1", "raw")
        widget = ExportWidget(mock_model, recording_path)

        with (
            patch("microemggui.widgets.export.export_step.sys") as mock_sys,
            patch(
                "microemggui.widgets.export.export_step.QFileDialog.getExistingDirectory",
                return_value="",
            ) as mock_dialog,
        ):
            mock_sys.frozen = True
            mock_sys._MEIPASS = fake_meipass
            widget.browse_for_export_folder()
            call_args = mock_dialog.call_args
            assert call_args[0][2] == os.path.expanduser("~")
