import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from FileScanner_pipeline.scan_dir.create_samplesheet import update_samplesheet

@pytest.fixture
def mock_samplesheet():
    samplesheet = MagicMock(spec=Samplesheet)
    samplesheet.get_metadata.return_value = {
        "dir": "/mock/dir",
        "model": "mock_model",
        "outputLocation": "mock_output"
    }
    samplesheet.file_belongs_to_samplesheet.return_value = False
    samplesheet.add_file.return_value = True
    return samplesheet

@pytest.fixture
def mock_bar():
    bar = MagicMock()
    bar.progress_bar = "mock_progress_bar"
    return bar

@pytest.fixture
def mock_telegram_bar():
    telegram_bar = MagicMock()
    return telegram_bar

def test_update_samplesheet(mock_samplesheet, mock_bar, mock_telegram_bar):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock .pod5 files
        pod5_file_1 = Path(temp_dir) / "file1.pod5"
        pod5_file_2 = Path(temp_dir) / "file2.pod5"
        pod5_file_1.touch()
        pod5_file_2.touch()

        mock_samplesheet.get_metadata.return_value["dir"] = temp_dir

        with patch('FileScanner_pipeline.scan_dir.create_samplesheet.list_pod5', return_value=[str(pod5_file_1), str(pod5_file_2)]):
            with patch('FileScanner_pipeline.scan_dir.create_samplesheet.prepare_pod5_inspect_argparser') as mock_parser:
                mock_args = MagicMock()
                mock_args.command = 'debug'
                mock_args.input_files = [pod5_file_1, pod5_file_2]
                mock_parser.return_value.parse_args.return_value = mock_args

                added_files = update_samplesheet(mock_samplesheet, mock_bar, mock_telegram_bar)

                assert added_files == 2
                mock_samplesheet.add_file.assert_called()
                mock_samplesheet.update_json_file.assert_called_once()
                mock_bar.increase.assert_called()
                mock_telegram_bar.telegram_send_bar.assert_called()

def test_update_samplesheet_no_new_files(mock_samplesheet, mock_bar, mock_telegram_bar):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock .pod5 files
        pod5_file_1 = Path(temp_dir) / "file1.pod5"
        pod5_file_1.touch()

        mock_samplesheet.get_metadata.return_value["dir"] = temp_dir
        mock_samplesheet.file_belongs_to_samplesheet.return_value = True

        with patch('FileScanner_pipeline.scan_dir.create_samplesheet.list_pod5', return_value=[str(pod5_file_1)]):
            added_files = update_samplesheet(mock_samplesheet, mock_bar, mock_telegram_bar)

            assert added_files == 0
            mock_samplesheet.add_file.assert_not_called()
            mock_samplesheet.update_json_file.assert_called_once()
            mock_bar.increase.assert_called()
            mock_telegram_bar.telegram_send_bar.assert_called()