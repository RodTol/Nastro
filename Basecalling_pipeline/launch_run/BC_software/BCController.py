import os
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from samplesheet_check.samplesheet_api import Samplesheet

def print_node_name():
    node_name = os.getenv('SLURMD_NODENAME')
    if node_name:
        print(f"Node Name: {node_name}")
    else:
        print("SLURMD_NODENAME environment variable is not set. Are you running under SLURM?")


class BCController:
    """
    Class that represents a controller that checks if the basecalling task is finished by looking
    at an input samplesheet. This object will also launch a new run of the basecalling run
    with the same parameters

    We will not wait for BCP to close automatically. Immediatly after the samplesheet is updated
    (so when BCM makes a completed_work() call) everything will shutdown
    """

    def __init__(self, BCM_pid, BCP_pid, Dorado_pid, samplesheet):
        """
        Initialize the BCController object by taking the BCP, BCM and dorado server PIDs and also
        the samplesheet path.
        @param *_pid - pid for each of the process to manage
        @param samplesheet - path to the samplesheet
        @return None
        """
        #Debugging print
        print("*************BCController READ FROM JSON*************")
        self.BCM_pid = BCM_pid
        self.BCP_pid = BCP_pid
        self.Dorado_pid = Dorado_pid
        self.samplesheet = Samplesheet(samplesheet)
        print_node_name()
        print(f"With the following PIDs:\n BCM_pid={self.BCM_pid}\n BCP_pid={self.BCP_pid}\n Dorado_pid={self.Dorado_pid}")

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


if __name__ == '__main__':
    BCM_pid = sys.argv[1]
    BCP_pid = sys.argv[2]
    Dorado_pid = sys.argv[3]
    samplesheet = sys.argv[4]
    bc_processor = BCController(BCM_pid, BCP_pid, Dorado_pid, samplesheet)