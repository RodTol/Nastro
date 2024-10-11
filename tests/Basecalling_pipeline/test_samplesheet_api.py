import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet, create_samplesheet_entry

# Fixture for a valid sample JSON data
@pytest.fixture
def valid_sample_data():
    return {
        "metadata": {
            "dir": "/path/to/dir",
            "model": "model_name",
            "outputLocation": "/path/to/output"
        },
        "files": [
            {
                "name": "file1.fast5",
                "path": "/path/to/file1.fast5",
                "size(GB)": 1.5,
                "basecalled": "False",
                "aligned": "False",
                "run_id": "run_1"
            }
        ]
    }

# Test for _verify_samplesheet method
def test_verify_samplesheet(valid_sample_data, tmp_path):
    # Create a temporary JSON file
    json_file = tmp_path / "test_samplesheet.json"
    with open(json_file, 'w') as f:
        json.dump(valid_sample_data, f)
    
    # Create Samplesheet instance
    samplesheet = Samplesheet(str(json_file))
    
    # Test _verify_samplesheet method
    assert samplesheet._verify_samplesheet(valid_sample_data) == True

    # Test with invalid data
    invalid_data = valid_sample_data.copy()
    del invalid_data["metadata"]
    assert samplesheet._verify_samplesheet(invalid_data) == False

# Test for create_samplesheet_entry function
def test_create_samplesheet_entry(tmp_path):
    # Create a temporary file
    test_file = tmp_path / "test_file.fast5"
    test_file.write_text("This is a test file")
    
    # Test create_samplesheet_entry function
    entry = create_samplesheet_entry(str(test_file))
    
    assert entry is not None
    assert entry["name"] == "test_file.fast5"
    assert entry["path"] == str(test_file)
    assert "size(GB)" in entry
    assert entry["basecalled"] == False
    assert entry["aligned"] == False
    assert entry["run_id"] == ""

    # Test with non-existent file
    non_existent_entry = create_samplesheet_entry("/path/to/non_existent_file.fast5")
    assert non_existent_entry is None

# Test for file_belongs_to_samplesheet method
def test_file_belongs_to_samplesheet(valid_sample_data, tmp_path):
    json_file = tmp_path / "test_samplesheet.json"
    with open(json_file, 'w') as f:
        json.dump(valid_sample_data, f)
    
    samplesheet = Samplesheet(str(json_file))
    
    assert samplesheet.file_belongs_to_samplesheet("/path/to/non_existent_file.fast5") == False

# Test for check_basecalling_is_finished method
def test_check_basecalling_is_finished(valid_sample_data, tmp_path):
    json_file = tmp_path / "test_samplesheet.json"
    with open(json_file, 'w') as f:
        json.dump(valid_sample_data, f)
    
    samplesheet = Samplesheet(str(json_file))
    
    assert samplesheet.check_basecalling_is_finished() == False
    
    # Modify the data to set basecalled to True
    samplesheet.data["files"][0]["basecalled"] = "True"
    samplesheet.update_json_file()
    
    assert samplesheet.check_basecalling_is_finished() == True
