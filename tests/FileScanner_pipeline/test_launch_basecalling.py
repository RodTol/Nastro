import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
from FileScanner_pipeline.scan_dir.launch_basecalling_run import launch_run

@pytest.fixture
def mock_samplesheet():
    mock_samplesheet = MagicMock(spec=Samplesheet)
    mock_samplesheet.get_metadata.return_value = {
        "outputLocation": "/mock/output/location"
    }
    mock_samplesheet.file_path = "/mock/samplesheet/path"
    return mock_samplesheet

@pytest.fixture
def mock_jenkins_trigger():
    with patch('FileScanner_pipeline.scan_dir.launch_basecalling_run.Jenkins_trigger') as mock_jenkins_trigger:
        yield mock_jenkins_trigger

@pytest.fixture
def mock_makedirs():
    with patch('FileScanner_pipeline.scan_dir.launch_basecalling_run.os.makedirs') as mock_makedirs:
        yield mock_makedirs

def test_launch_run(mock_samplesheet, mock_makedirs, mock_jenkins_trigger):
    # Mock Jenkins_trigger instance
    mock_jenkins_instance = mock_jenkins_trigger.return_value
    mock_jenkins_instance.start_job = MagicMock()

    # Call the function
    launch_run(mock_samplesheet)

    # Check if directories were created
    mock_makedirs.assert_any_call('/mock/output/location/input', exist_ok=True)
    mock_makedirs.assert_any_call('/mock/output/location/logs', exist_ok=True)
    mock_makedirs.assert_any_call('/mock/output/location/output', exist_ok=True)

    # Check if Jenkins job was started with correct parameters
    expected_parameters = {
        "pathToSamplesheet": "/mock/samplesheet/path",
        "pathToInputDir": "/mock/output/location/input",
        "pathToOutputDir": "/mock/output/location/output",
        "pathToLogsDir": "/mock/output/location/logs",
        "RUN_TESTING_CLEANUP": False
    }
    mock_jenkins_instance.start_job.assert_called_once_with(
        'tolloi/Pipeline_long_reads/basecalling_pipeline', 'kuribo', expected_parameters
    )

def test_launch_run_no_output_location(mock_samplesheet, mock_makedirs, mock_jenkins_trigger):
    # Modify the mock to return no output location
    mock_samplesheet.get_metadata.return_value = {}

    # Call the function
    with pytest.raises(KeyError):
        launch_run(mock_samplesheet)

    # Ensure no directories were created
    mock_makedirs.assert_not_called()

    # Ensure no Jenkins job was started
    mock_jenkins_trigger.return_value.start_job.assert_not_called()

def test_launch_run_invalid_samplesheet(mock_makedirs, mock_jenkins_trigger):
    # Create a mock Samplesheet with invalid data
    mock_samplesheet = MagicMock(spec=Samplesheet)
    mock_samplesheet.get_metadata.side_effect = Exception("Invalid samplesheet")

    # Call the function
    with pytest.raises(Exception, match="Invalid samplesheet"):
        launch_run(mock_samplesheet)

    # Ensure no directories were created
    mock_makedirs.assert_not_called()

    # Ensure no Jenkins job was started
    mock_jenkins_trigger.return_value.start_job.assert_not_called()