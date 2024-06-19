import os
import json 

class runParameters:
    def __init__(self, id, input_dir, output_dir, logs_dir, basecalling_model, ideal_size=None, actual_size=None, run_config_path=None):
        self.id = id
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logs_dir = logs_dir
        self.basecalling_model = basecalling_model
        self.ideal_size = ideal_size
        self.actual_size = actual_size
        self.config_path = run_config_path

    def __str__(self):
        return (f"runParameters:\n"
                f"  ID: {self.id}\n"
                f"  Input: {self.input_dir}\n"
                f"  Output Directory: {self.output_dir}\n"
                f"  Logs Directory: {self.logs_dir}\n"
                f"  Basecalling Model: {self.basecalling_model}\n"
                f"  Ideal size: {self.ideal_size}\n"
                f"  Actual size: {self.actual_size}\n"
                f"  Config file: {self.config_path}")

    def create_run_input_symlinks(self, files_list):
        '''
        This function will create a symlink for each file 
        contained in the files_list. Note that the files_list needs
        to be a list of dict as performed by the Samplesheet
        '''
        for file in files_list:
            create_symlink(file["path"], self.input_dir)
    
    def to_dict(self):
        '''
        Conversion of the class to JSON format in order to
        simplify the printing and reading of a object of this class
        '''
        return {
            'id': self.id,
            'input_dir': self.input_dir,
            'output_dir': self.output_dir,
            'logs_dir': self.logs_dir,
            'basecalling_model': self.basecalling_model,
            'ideal_size': self.ideal_size,
            'actual_size': self.actual_size,
            'config_path': self.config_path
        }

    def write_to_file(self, file_path):
        '''
        Write down the object
        '''
        with open(file_path, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)
        print("Run params written at ", file_path)            

    @classmethod
    def from_file(cls, file_path):
        '''
        Create an instance by reading a file
        '''
        with open(file_path, 'r') as file:
            data = json.load(file)
            return cls(
                id=data.get('id'),
                input_dir=data.get('input_dir'),
                output_dir=data.get('output_dir'),
                logs_dir=data.get('logs_dir'),
                basecalling_model=data.get('basecalling_model'),
                ideal_size=data.get('ideal_size'),
                actual_size=data.get('actual_size'),
                run_config_path=data.get('config_path')
            )

    def update_from_file(self, file_path):
        '''
        Update an instance by reading a file
        '''
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.id = data.get('id', self.id)
            self.input_dir = data.get('input_dir', self.input_dir)
            self.output_dir = data.get('output_dir', self.output_dir)
            self.logs_dir = data.get('logs_dir', self.logs_dir)
            self.basecalling_model = data.get('basecalling_model', self.basecalling_model)
            self.ideal_size = data.get('ideal_size', self.ideal_size)
            self.actual_size = data.get('actual_size', self.actual_size)
            self.config_path = data.get('config_path', self.config_path)            


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