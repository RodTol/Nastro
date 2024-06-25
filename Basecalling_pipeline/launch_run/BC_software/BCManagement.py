import json
import os
import sys
import shutil
import threading
import time
import uuid
from flask import Flask, request, jsonify
from collections import namedtuple
from BCConfiguration import Conf

BCStatus = namedtuple("BCStatus", ["ASSIGNED", "STARTED", "PROCESSING", "STOPPED", "DONE", "FAILED"])
bc_status = BCStatus("ASSIGNED", "STARTED", "PROCESSING", "STOPPED", "DONE", "FAILED")

class BCBatch:
    """
    Class that represents a batch of pod5 files that have been assigned for processing.

    It consists of:
    - jobid           int assigned to the job
    - job_input_dir   string with the name of the directory RELATIVE TO the dorado server's INPUTDIR that
                      contains symlinks to the pod5 files that need to be processed.
    - job_output_dir  string with the name of the directory RELATIVE TO the dorado server's OUTPUTDIR that
                      will contain the output FASTQ files.
    - bc_engine_id    string identifying the dorado server that was assigned to the processing
    - batch_size      int actual size of the batch, which may differ from the requested size if there weren't
                      enough files to fill the request.
    - batch           list with the actual filenames
    """

    def __init__(self, report_back_period=300, jobid="-1", job_input_dir="", job_output_dir="", bc_engine_id="", batch_size=0, batch=None):
        if batch is None:
            batch = []

        self.report_back_period = report_back_period
        self.jobid = jobid
        self.job_input_dir = job_input_dir
        self.job_output_dir = job_output_dir
        self.bc_engine_id = bc_engine_id
        self.batch_size = batch_size
        self.batch = batch


class BCWorkloadState:
    """
    Class that represents the state of the basecalling processing, as well as
    providing methods for operating on it.  

    It consist of :
    - INPUTDIR              path to the dir containing all the raw .POD5 files.
    - OUTPUTDIR             path to the dir where the basecalling should direct its output for this job.
    - unassigned_bc         list of file that still need to be basecalled
    - default_batch_size    default size of the batch 
    - assigned_batches      the actual batch of file
    """
    def __init__(self, json_file_path, node_index):
        """
        Initialize the BCMReader class with the provided JSON file path and node index.
        
        @param json_file_path - the path to the JSON file
        @param node_index - the index of the node
        """
        print("*************BCM READ FROM JSON*************")
        conf = Conf.from_json(json_file_path, node_index)

        self.INPUTDIR = conf.mngt_inputdir
        self.OUTPUTDIR = conf.mngt_outputdir
        self.unassigned_bc = []
        self.default_batch_size = conf.mngt_batch_size
        self.assigned_batches = {}

    def update(self):
        """
        Method used to tell this BCWorkloadStatus to read the filesystem and update itself
        accordingly.

        The intended use case is scanning for the presence of new pod5 files to process, as
        well as reconstruct the internal state in case of a crash, based on what it finds in
        the filesystem.

        @return True if the update is successful, False if there are any errors.
        """
        # find all processed files i.e. get  list of all .FASTQ files
        fastq_files = []
        passoutputdir = os.path.join(self.OUTPUTDIR, "pass")
        failoutputdir = os.path.join(self.OUTPUTDIR, "fail")
        for dir_entry in (passoutputdir, failoutputdir):
            for entry in os.scandir(dir_entry):
                if entry.is_file():
                    str_name = entry.name
                    if (len(str_name)>6) & (str_name[-6:].lower() == ".fastq"):
                        fastq_files.append(str_name[:-6])
        # find all raw files that do not have a FASTQ counterparty,
        # as well as all files that have been assigned for processing
        potential_files = [] # pod5 files for which there is no fastq counterparty
        assigned_files = [] # pod5 files assigned for basecalling
        for entry in os.scandir(self.INPUTDIR):
            if entry.is_dir():
                # It's a dir: it should contain symlinks to assigned files that are being worked on
                str_dirname = entry.name
                if (len(str_dirname)>8 & (str_dirname[:8]=="ASSIGNED")) | (len(str_dirname)>6 & (str_dirname[:6]=="FAILED")):
                    for assignment in os.scandir(entry):
                        # check assigned file is a symlink!
                        if assignment.is_symlink():
                            # check it ends with .pod5
                            str_assignment = assignment.name
                            if len(str_assignment)>5 & (str_assignment[-5:].lower() == ".pod5"):
                                # add it to the list
                                assigned_files.append(str_assignment[:-5])
            elif entry.is_file():
                # It's a file: it should be a pod5 file that potentially needs to be processed unless already assigned
                str_name = entry.name
                if len(str_name)>5 & (str_name[-5:].lower() == ".pod5"):
                    str_name = str_name[:-5]
                    if str_name not in fastq_files:
                        potential_files.append(str_name)
        # filter assigned_files from potential_files
        final_list = []
        for entry in potential_files:
            if entry not in assigned_files:
                final_list.append(entry+".pod5")
        # update this instance
        self.unassigned_bc = final_list
        #TO DO: reconstruct assigned_batches after crash?

    def assign_work_to(self, bc_engine_id="default-engine", batch_size=0):
        """
        Method invoked to assign work to the supplied dorado_server. By default, the dorado_server's
        inbuilt desired batch size will be used; but optionally this can be overriden through the
        batch_size parameter.

        Note that if there aren't enough pending files to meet the required batch size, the request
        is still successful and the dorado_server will be assigned all available ones.

        Finally, a zero or negative value of batch_size will automatically imply the use of the
        dorado_server's inbuilt default batch size.

        @param bc_engine_id - the ID of the Dorado server to assign work to
        @param batch_size - optional integer specifying the desired batch size

        @return BCBatch object containing details of the assigned work
        """

        # if there is nothing left to process, return an EMPTY BCBatch
        if len(self.unassigned_bc) == 0:
            return BCBatch()
        # use default batch_size if no batch_size is specified
        if batch_size <= 0:
            batch_size = self.default_batch_size
        # set batch_size to the min between the desired batch size and available files
        batch_size = min(batch_size, len(self.unassigned_bc))
        # get the files
        batch = [self.unassigned_bc.pop(0) for x in range(batch_size)]
        # choose a new jobid
        jobid = str(uuid.uuid4().int)
        # prepare the input dir name for the job
        job_input_dir = "_".join(["ASSIGNED", str(jobid), bc_engine_id])
        # transactionally create in one go the dir and symlinks
        # TO DO! TRANSACTION !!!
        dirfullpath = os.path.join(self.INPUTDIR, job_input_dir)
        os.mkdir(dirfullpath)
        for fl in batch:
            os.symlink(os.path.join(self.INPUTDIR, fl), os.path.join(dirfullpath, fl))
        # prepare temporary output dir
        job_output_dir = "_".join(["TMPOUTPUT", str(jobid), bc_engine_id])
        outputdirfullpath = os.path.join(self.OUTPUTDIR, job_output_dir)
        os.mkdir(outputdirfullpath)
        # return the BCBatch
        bc_work = BCBatch(jobid=jobid, job_input_dir=job_input_dir, job_output_dir=job_output_dir, bc_engine_id=bc_engine_id, batch_size=batch_size, batch=batch)
        self.assigned_batches[jobid] = bc_work
        return bc_work

    def completed_work(self, jobid="", jobstate=""):
        """
        Method invoked to complete the processing of a batch for a given job. It is based on its
        state and updates the directories accordingly.

        @param jobid - The ID of the job being completed.
        @param jobstate - The state of the job (FAILED, DONE, or UNKNOWN).
        
        """
        # MAKE IT A TRANSACTION IN CASE OF CRASH
        bc_work = self.assigned_batches.pop(jobid)
        full_job_input_dir = os.path.join(self.INPUTDIR, bc_work.job_input_dir)
        full_job_output_dir = os.path.join(self.OUTPUTDIR, bc_work.job_output_dir)
        if jobstate == bc_status.FAILED:
            # rename inputdir to FAILED so it can be excluded from reassignment until manual intervention
            failed_full_job_input_dir = os.path.join(self.INPUTDIR, bc_work.job_input_dir.replace("ASSIGNED","FAILED"))
            failed_full_job_output_dir = os.path.join(self.OUTPUTDIR, bc_work.job_output_dir.replace("TMPOUTPUT","FAILEDOUTPUT"))
            os.rename(full_job_input_dir, failed_full_job_input_dir)
            os.rename(full_job_output_dir, failed_full_job_output_dir)
        elif jobstate == bc_status.DONE:
            #everything went all right
            passdir = os.path.join(full_job_output_dir,'pass')
            destpassdir = os.path.join(self.OUTPUTDIR, 'pass')
            if os.path.exists(passdir) & os.path.exists(destpassdir):
                for entry in os.scandir(passdir):
                    str_name = "job_id_" + jobid + "_" + entry.name #added jobid tag
                    dst = os.path.join(destpassdir, str_name)
                    os.rename(entry.path, dst)  # it will move the fastq file to the final destination
            faildir = os.path.join(full_job_output_dir,'fail')
            destfaildir = os.path.join(self.OUTPUTDIR, 'fail')
            if os.path.exists(faildir) & os.path.exists(destfaildir):
                for entry in os.scandir(faildir):
                    str_name = "job_id_" + jobid + "_" + entry.name #added jobid tag
                    dst = os.path.join(destfaildir, str_name)
                    os.rename(entry.path, dst)  # it will move the fastq file to the final destination
            shutil.rmtree(full_job_input_dir)
            log_full_job_output_dir = os.path.join(self.OUTPUTDIR, bc_work.job_output_dir.replace("TMPOUTPUT", "LOGOUTPUT"))
            os.rename(full_job_output_dir, log_full_job_output_dir)
        else:
            print("ATTENTION! UNKNOWN STATE FROM CLIENT! " + jobstate)
            unknown_full_job_input_dir = os.path.join(self.INPUTDIR, bc_work.job_input_dir.replace("ASSIGNED","UNKNOWN"))
            unknown_full_job_output_dir = os.path.join(self.OUTPUTDIR, bc_work.job_output_dir.replace("TMPOUTPUT","UNKNOWNOUTPUT"))
            os.rename(full_job_input_dir, unknown_full_job_input_dir)
            os.rename(full_job_output_dir, unknown_full_job_output_dir)


class BCManager:
    """
    A class representing a RESTful Service for managing Basecalling work requests from Basecalling Engines.

    @param json_file_path - The path to the JSON file.
    @param node_index - The index of the node.
    @param shutdown_interval - The interval for shutting down.
    """

    def __init__(self,json_file_path, node_index, shutdown_interval=100):
        """
        Initialize the class with the provided parameters.

        @param json_file_path - the path to the JSON file
        @param node_index - the index of the node in the node list provided by the JSON
        @param shutdown_interval - the interval for shutdown (default is 100)
        """
        self.lock = threading.Lock()
        self.tracker = {} # dict of job_id -> [last_ack_time, state, report_back_period]
        self.bc_state = BCWorkloadState(json_file_path, node_index)
        self.bc_state.update()
        self.app = Flask(__name__)
        a = self.app
        
        self.shutdown_interval = shutdown_interval
        self.last_activity_time = time.time()

        """
        Define a route "/assignwork" that handles GET requests to assign work to an engine. It takes in
        the batch size and engine ID from the request parameters. It then assigns work to the specified
        engine, updates the assignment report interval, and tracks the job status.
         
        Finally, it returns the assignment reply in JSON format.

        @return JSON response with the assignment reply.
        """
        # /assignwork
        @a.route("/assignwork", methods=["GET"])
        def get_assignwork():
            req_batchsize = int(request.args['batchsize'])
            req_engineid = request.args['engineid']
            with self.lock:
                assignment_reply = self.bc_state.assign_work_to(req_engineid, req_batchsize)
                assignment_reply.report_back_interval = 90 # maximum seconds that will be waited for keep alive from client
                self.tracker[assignment_reply.jobid] = [time.time(), bc_status.ASSIGNED, 90]
            self.update_last_activity_time()    #update activy time 
            return json.dumps(assignment_reply.__dict__)

        """
        Define a route "/keepalive" that handles GET requests to keep a job alive. It takes in the
        job_id and the job_state from the request parameters.

        @return A JSON response indicating whether the job is late or not.
        """
        # /keepalive
        @a.route("/keepalive", methods=["GET"])
        def get_keepalive():
            req_job_id = request.args['job_id']
            req_job_state = request.args['job_state']
            with self.lock:
                entry = self.tracker[req_job_id].copy()
                right_now = time.time()
                entry[0] = right_now
                entry[1] = req_job_state
                # entry[2] stays the same
                self.tracker[req_job_id] = entry
            self.update_last_activity_time()    #update activy time 
            return json.dumps({"late": False})

        """
        Define a route that handles GET requests to retrieve completed job information. It 
        takes in the job_id, The ID of the completed job, and the job_state. Then it modify 
        the job_state by calling the method completed_work
        
        @return JSON response indicating the completion status.
        """
        # /completed
        @a.route("/completed", methods=["GET"])
        def get_completed():
            req_job_id = request.args['job_id']
            req_job_state = request.args['job_state']
            with self.lock:
                #
                # THIS SHOULD BE A TRANSACTION
                # if the req_job_id does not exist it is an unexpected error: inform client? how to handle it?
                del self.tracker[req_job_id]
                self.bc_state.completed_work(req_job_id, req_job_state)
            # NOTHING TO RETURN
            self.update_last_activity_time()    #update activy time 
            return json.dumps({"ok": True})    
        
        """
        Define a route '/heartbeat' that returns the status of the server based on the inactivity interval.
        GET request to check the server's status.

        @return JSON response with server status and inactivity interval.
        """
        # /heartbeat 
        @a.route('/heartbeat', methods=['GET'])
        def heartbeat():
            current_time = time.time()
            inactivity_interval = current_time - self.last_activity_time
            if inactivity_interval >= self.shutdown_interval:
                return jsonify({"status": "true", "inactivity_interval": inactivity_interval})
            else:
                return jsonify({"status": "false", "inactivity_interval": inactivity_interval})

    
    def update_last_activity_time(self):
        """
        Update the last_activity_time for when a /assignwork, /keepalive, /completed instance is called.
        
        @return None
        """
        with self.lock:
            self.last_activity_time = time.time()            
            
            
#Launching the flask server
#app.run decide on which host (0.0.0.0 means all) and port to listen
if __name__ == '__main__':
    json_file_path = sys.argv[1]
    node_index = int(sys.argv[2])
    RESTFulAPI = BCManager(json_file_path, node_index)
    RESTFulAPI.app.run(host='0.0.0.0', port=40765)



