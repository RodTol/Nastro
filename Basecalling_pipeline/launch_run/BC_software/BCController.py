import os
from datetime import datetime
import time
import psutil
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from samplesheet_check.samplesheet_api import Samplesheet
from subset_creation.pipelineInteract import Jenkins_trigger

def print_node_name():
    node_name = os.getenv('SLURMD_NODENAME')
    if node_name:
        print(f"Node Name: {node_name}", flush=True)
    else:
        print("SLURMD_NODENAME environment variable is not set. Are you running under SLURM?", flush=True)


class BCController:
    """
    Class that represents a controller that checks if the basecalling task is finished by looking
    at an input samplesheet. This object will also launch a new run of the basecalling run
    with the same parameters

    We will not wait for BCP to close automatically. Immediatly after the samplesheet is updated
    (so when BCM makes a completed_work() call) everything is shutted down
    """

    def __init__(self, run_params_path, BCM_pid, BCP_pid, Dorado_pid, samplesheet):
        """
        Initialize the BCController object by taking the BCP, BCM and dorado server PIDs and also
        the samplesheet path.
        @param *_pid - pid for each of the process to manage
        @param samplesheet - path to the samplesheet
        @return None
        """
        # Debugging print
        print("*************BCController*************", flush=True)
        self.run_params_path = run_params_path
        self.BCM_pid = BCM_pid
        self.BCP_pid = BCP_pid
        self.Dorado_pid = Dorado_pid
        self.samplesheet_path = samplesheet
        self.samplesheet = Samplesheet(samplesheet)

        # Load the JSON file
        with open(self.run_params_path, 'r') as file:
            config = json.load(file)

        # Run parameters
        self.run_name = config["id"]
        self.input_dir = os.path.dirname(config['input_dir'])
        self.output_dir = os.path.dirname(config['output_dir'])
        self.logs_dir = os.path.dirname(config['logs_dir'])

        self.assigned_reads = self._get_assigned_reads()
        self.jenkins = Jenkins_trigger()

        print_node_name()
        print(f"My PIDs:\n BCM_pid={self.BCM_pid}\n BCP_pid={self.BCP_pid}\n Dorado_pid={self.Dorado_pid}", flush=True)

    def _get_assigned_reads(self):
        assigned_reads = []
        for i, entry in enumerate(self.samplesheet.get_files()):
            if entry["basecalled"] == self.run_name:
                assigned_reads.append(i)
        return assigned_reads

    @staticmethod
    def return_datetime():
        """
        A static method that returns the current datetime in a specific format.
        @return The current datetime in the format "[%d/%b/%Y %H:%M:%S]"
        """
        # Get the current date and time
        current_datetime = datetime.now()
        # Format the datetime to [DD/Mon/YYYY HH:MM:SS]
        formatted_datetime = current_datetime.strftime("[%d/%b/%Y %H:%M:%S]")        
        return formatted_datetime

    def _is_pid_running(self, pid):
        """
        Check if a process with the given PID is running using psutil.
        @param pid: The process ID to check.
        @return: True if the process is running, otherwise False.
        """
        try:
            process = psutil.Process(int(pid))
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

    def _kill_process(self, pid):
        pid = int(pid)
        try:
            process = psutil.Process(pid)
            process.terminate()  # or process.kill() for immediate termination
            process.wait(timeout=3)  # Wait for the process to terminate
            print(f"Process {pid} terminated successfully.", flush=True)
        except psutil.NoSuchProcess:
            print(f"No process found with PID {pid}.", flush=True)
        except psutil.AccessDenied:
            print(f"Access denied to terminate process {pid}.", flush=True)
        except psutil.TimeoutExpired:
            print(f"Process {pid} did not terminate in time.", flush=True)
        except Exception as e:
            print(f"An error occurred: {e}", flush=True)
    
    def _launching_basecalling_pipeline(self):
        # Only the BCM hosting will launch the run
        jenkins_parameter =  {
            "pathToSamplesheet": self.samplesheet_path,
            "pathToInputDir": self.input_dir,
            "pathToOutputDir": self.output_dir, 
            "pathToLogsDir": self.logs_dir,
            "RUN_TESTING_CLEANUP": False
        }
        #print("Launching a new run with the following parameters:", flush=True)
        print(jenkins_parameter, flush=True)
        self.jenkins.start_job("tolloi/Pipeline_long_reads/basecalling_pipeline", "kuribo", jenkins_parameter)            

    def _launching_alignment_pipeline(self):
        jenkins_parameter =  {
            "pathToRunParams": self.run_params_path
        }
        print(jenkins_parameter, flush=True)
        self.jenkins.start_job("tolloi/Pipeline_long_reads/alignment_pipeline", "incal", jenkins_parameter)        

    def _shutdown_BCsoftware(self):
        print("Shutting down\n", flush=True)
        if self.BCM_pid != 'NULL':
            self._kill_process(self.BCM_pid) # BCM

            self._launching_basecalling_pipeline()
            self._launching_alignment_pipeline()

        self._kill_process(self.Dorado_pid) # Dorado
        sys.exit(0) # BCC

    def _check_samplesheet(self):
        print("Checking Samplesheet\n", flush=True)
        self.samplesheet.data = self.samplesheet.read_file()
        for i in self.assigned_reads:
            if self.samplesheet.get_files()[i]["basecalled"] != True:
                #print(f"File {self.samplesheet.get_files()[i]} still need to be basecalled", flush=True)
                return False
        return True

    def monitor_bcp_pid(self):
        """
        Monitor the BCP_pid and if it diseappears checks the assigned reads on
        the samplesheet. If even the samplesheet is completed initiate the shutdown
        """
        while True:
            if not self._is_pid_running(self.BCP_pid):
                print(f"At {self.return_datetime()} Process with PID {self.BCP_pid} has disappeared.", flush=True)
                if self._check_samplesheet():
                    self._shutdown_BCsoftware()
            time.sleep(1)  # Check every second


if __name__ == '__main__':
    run_params_path = sys.argv[1]
    BCM_pid = sys.argv[2]
    BCP_pid = sys.argv[3]
    Dorado_pid = sys.argv[4]
    samplesheet = sys.argv[5]
    bc_processor = BCController(run_params_path, BCM_pid, BCP_pid, Dorado_pid, samplesheet)
    bc_processor.monitor_bcp_pid()
