import requests
import time
import os
import subprocess
from datetime import datetime
import sys
from BCConfiguration import Conf

class BCController:
    """
    Class that represents a controller that checks if the Basecalling infrastructure is still working
    and if it is not, shutdown the whole process. The shutdown will be performed by killing the slurm
    job

    In order to do this, it will periodically ask for an 'heartbeat' and see if the inactivity
    time is higher than a specified threshold, specified in BCManagement (shutdown_interval=100)
    """

    def __init__(self, json_file_path, node_index):
        """
        Initialize the BCController object by reading configuration from a JSON file and setting up initial values.
        @param json_file_path - the path to the JSON file containing configuration
        @param node_index - the index of the node
        @return None
        """
        #Debugging print
        print("*************BCController READ FROM JSON*************")
        conf = Conf.from_json(json_file_path, node_index)
        self.last_heartbeat_time = time.time()
        self.heartbeat_url = conf.heartbeat_url
        #Getting the job id of the slurm job
        self.slurm_job_id = os.environ.get('SLURM_JOB_ID')
    
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

    def check_heartbeat(self):
        """
        Check the heartbeat status by sending a request to the specified URL in the settings.
        @return True if the inactivity is higher than threshold, False if it's lower, None otherwise.
        """
        try:
            # Send a request to BCManagement to get the current heartbeat time
            response = requests.get(self.heartbeat_url)            
            if response.ok:
                data = response.json()
                status = data.get("status")
                inactivity_interval=data.get("inactivity_interval")
                #Inactivity is higher than allowed threshold
                if status == "true": 
                    self.last_heartbeat_time = time.time()
                    print(self.return_datetime(), '- - Heart stopped. Basecalling has finished. Inactivity interval: ', inactivity_interval, flush=True)
                    # Return True to start shutdown routine
                    return True
                #Inactivity is lower than allowed threshold
                elif status == "false":
                    self.last_heartbeat_time = time.time()
                    print(self.return_datetime(), '- - Heartbeat received. Basecalling still in progress. Inactivity interval: ', inactivity_interval, flush=True)
                    return False
            else:
                print(self.return_datetime(), '- - Error: Unexpected response from BCManagement server.', flush=True)
        except requests.RequestException:
            print(self.return_datetime(), '- - Error: Failed to connect to BCManagement server.', flush=True)
    
    def monitor_heartbeat(self):
        """
        Monitor the heartbeat continuously and starts the shutdown if the heartbeat returns a True value.
        """
        while True:
            # Check the heartbeat. True means it need to be shutted down
            status=self.check_heartbeat()
            if status:
                print(self.return_datetime(), '- - Shutdown', flush=True)
                # Triggers shutdown process of itself
                self.cancel_slurm_job()
                break

            time.sleep(30)  # Check heartbeat every 30 seconds    

    def cancel_slurm_job(self):
        """
        Cancel a SLURM job using its job ID.
        """
        if self.slurm_job_id:
            # Shutdown routine
            try:
                subprocess.run(['scancel', self.slurm_job_id])
                print(f"SLURM job {self.slurm_job_id} successfully canceled.")
            except subprocess.CalledProcessError as e:
                print(f"Error canceling SLURM job {self.slurm_job_id}: {e}")
        else:
            print("SLURM_JOB_ID not found in environment variables.")


if __name__ == '__main__':
    json_file_path = sys.argv[1]
    node_index = int(sys.argv[2])
    bc_processor = BCController(json_file_path, node_index)
    bc_processor.monitor_heartbeat()