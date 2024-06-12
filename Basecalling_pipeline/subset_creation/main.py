import sys
import os
import hashlib
import datetime

from subset_creator import Subsetter

class mainParameters:
    def __init__(self, samplesheet, input_dir, output_dir, logs_dir, basecalling_model):
        self.samplesheet = samplesheet
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logs_dir = logs_dir
        self.basecalling_model = basecalling_model

    def __str__(self):
        return (f"mainParameters:\n"
                f"  Samplesheet: {self.samplesheet}\n"
                f"  Input Directory: {self.input_dir}\n"                
                f"  Output Directory: {self.output_dir}\n"
                f"  Logs Directory: {self.logs_dir}\n"
                f"  Basecalling Model: {self.basecalling_model}")

class runParameters:
    def __init__(self, id, input_dir, output_dir, logs_dir, basecalling_model):
        self.id = id
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logs_dir = logs_dir
        self.basecalling_model = basecalling_model

    def __str__(self):
        return (f"runParameters:\n"
                f"  ID: {self.id}\n"
                f"  Input: {self.input_dir}\n"
                f"  Output Directory: {self.output_dir}\n"
                f"  Logs Directory: {self.logs_dir}\n"
                f"  Basecalling Model: {self.basecalling_model}")

    def create_run_input_symlinks(self, files_list):
        '''
        This function will create a symlink for each file 
        contained in the files_list. Note that the files_list needs
        to be a list of dict as performed by the Samplesheet
        '''
        for file in files_list:
            create_symlink(file["path"], self.input_dir)

def create_symlink(target_path, link_directory, link_name=None):
    """
    Creates a symbolic link for the target_path in the specified link_directory.

    :param target_path: The path to the target file or directory.
    :param link_directory: The directory where the symlink will be created.
    :param link_name: The name of the symlink. If None, the name of the target_path will be used.
    :return: The path of the created symlink.
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"The target path {target_path} does not exist.")
    if not os.path.isdir(link_directory):
        raise NotADirectoryError(f"The link directory {link_directory} does not exist or is not a directory.")

    if link_name is None:
        link_name = os.path.basename(target_path)
    
    symlink_path = os.path.join(link_directory, link_name)
    os.symlink(target_path, symlink_path)
    
    return symlink_path


def generate_short_hash(input_str):
    return hashlib.sha256(input_str.encode()).hexdigest()[:8]

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 main.py path/to/file.json path/to/input/root/dir path/to/output/root/dir path/to/logs/root/dir basecalling model")
        sys.exit(1)
    
    main_params = mainParameters(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    print(main_params)

    run_params = runParameters('','','','','')
    #Create batch hash identifier
    time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    run_params.id = generate_short_hash(time)
    #Create input dir for the run
    run_params.input_dir = os.path.join(run_params.id, main_params.input_dir)
    #Create the actual subset inside the input dir
    subsetter = Subsetter(main_params.samplesheet)
    run_subset = subsetter.create_subset(run_params.id)
    run_params.create_run_input_symlinks(run_subset)
    #Create output dir for the run
    run_params.output_dir = os.path.join(run_params.id, main_params.output_dir)
    #Create logs dir for the run
    run_params.logs_dir = os.path.join(run_params.id, main_params.logs_dir)
    #Set basecalling model
    run_params.basecalling_model = main_params.basecalling_model
    print(run_params)
    
    #Create config file