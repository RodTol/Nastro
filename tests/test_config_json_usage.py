from Basecalling_pipeline.launch_run.create_sbatch_file import *

def test_correct_reading() -> None:
    '''
    Testing if a correct file is correctly read XD
    '''
    path = "test_files/config_correct.json"
    assert check_json_structure(path) == True

def test_error_detection() -> None:
    '''
    Testing if a incorrect file is detected
    '''
    path = "test_files/config_missing_field.json"
    assert check_json_structure(path) == False
