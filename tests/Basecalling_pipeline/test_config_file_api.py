import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Basecalling_pipeline.subset_creation.config_file_api import General, Slurm, Basecalling, ComputingResources, ConfigFile

# Mock ConfigFile for testing
class MockConfigFile:
    def __init__(self):
        self.data = {
            'General': {},
            'Slurm': {},
            'Basecalling': {},
        }

@pytest.fixture
def mock_config_file():
    return MockConfigFile()

def test_general_class(mock_config_file):
    general = General(mock_config_file, "Test Run", "2023-06-01")
    
    assert general.name == "Test Run"
    assert general.run_time == "2023-06-01"
    
    general.name = "Updated Run"
    assert general.name == "Updated Run"
    assert mock_config_file.data['General']['name'] == "Updated Run"
    
    assert general.to_dict() == {"name": "Updated Run", "run_time": "2023-06-01"}

def test_slurm_class(mock_config_file):
    slurm = Slurm(mock_config_file, "/output", "/error", "main.py")
    
    assert slurm.output_path == "/output"
    assert slurm.error_path == "/error"
    assert slurm.main_script == "main.py"
    
    slurm.output_path = "/new_output"
    assert slurm.output_path == "/new_output"
    assert mock_config_file.data['Slurm']['output_path'] == "/new_output"
    
    assert slurm.to_dict() == {"output_path": "/new_output", "error_path": "/error", "main_script": "main.py"}

def test_basecalling_class(mock_config_file):
    basecalling = Basecalling(mock_config_file, "model1", "/input", "/output", "/logs", "/supervisor.py")
    
    assert basecalling.model == "model1"
    assert basecalling.input_dir == "/input"
    assert basecalling.output_dir == "/output"
    assert basecalling.logs_dir == "/logs"
    assert basecalling.supervisor_script_path == "/supervisor.py"
    
    basecalling.model = "model2"
    assert basecalling.model == "model2"
    assert mock_config_file.data['Basecalling']['model'] == "model2"
    
    assert basecalling.to_dict() == {
        "model": "model2",
        "input_dir": "/input",
        "output_dir": "/output",
        "logs_dir": "/logs",
        "supervisor_script_path": "/supervisor.py"
    }

def test_computing_resources_class(mock_config_file):
    resources = ComputingResources(
        mock_config_file, "host1", "8080", ["queue1"], ["node1"], ["192.168.1.1"],
        ["4"], ["8GB"], ["1"], ["GPU1"], ["100"]
    )
    
    assert resources.index_host == "host1"
    assert resources.port == "8080"
    assert resources.nodes_queue == ["queue1"]
    assert resources.nodes_list == ["node1"]
    assert resources.nodes_ip == ["192.168.1.1"]
    assert resources.nodes_cpus == ["4"]
    assert resources.nodes_mem == ["8GB"]
    assert resources.nodes_gpus == ["1"]
    assert resources.gpus == ["GPU1"]
    assert resources.batch_size_list == ["100"]
    
    resources.index_host = "host2"
    assert resources.index_host == "host2"
    assert mock_config_file.data['index_host'] == "host2"
    
    assert resources.to_dict() == {
        "index_host": "host2",
        "port": "8080",
        "nodes_queue": ["queue1"],
        "nodes_list": ["node1"],
        "nodes_ip": ["192.168.1.1"],
        "nodes_cpus": ["4"],
        "nodes_mem": ["8GB"],
        "nodes_gpus": ["1"],
        "gpus": ["GPU1"],
        "batch_size_list": ["100"]
    }


def test_config_file_class_invalid_file(tmp_path):
    # Create a temporary file with an invalid extension
    invalid_file_path = tmp_path / "test_config.txt"
    invalid_file_path.touch()

    # Test that an exception is raised when trying to read an invalid file
    with pytest.raises(ValueError) as exc_info:
        ConfigFile(str(invalid_file_path))
    assert "Invalid file extension" in str(exc_info.value)

def test_config_file_class_missing_file(tmp_path):
    # Test that an exception is raised when the file doesn't exist
    missing_file_path = tmp_path / "missing_config.json"
    with pytest.raises(FileNotFoundError) as exc_info:
        ConfigFile(str(missing_file_path))
    assert "File not found" in str(exc_info.value)

