# Copyright 2024 Area Science Park
# Author: Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

class Conf:
    """
    Class that collects all configurable parameters.
    """

    mngt_batch_size = 3
    mngt_outputdir = ''
    mngt_inputdir = ''

    request_work_url = 'http://127.0.0.1:57967/assignwork'
    
    engine_external_script = ''
    engine_outputdir = ''
    engine_inputdir = ''
    engine_polling_interval = 1 
    engine_id = ''
    engine_optimal_request_size = 100
    engine_model = ''
    
    keep_alive_terminate_url = "http://127.0.0.1:57967/completed"
    keep_alive_url = "http://127.0.0.1:57967/keepalive"

    @classmethod
    def from_json(cls, file_path, node_index):
        """
        Initialize the Conf class from a JSON file.

        Args:
            file_path (str): Path to the JSON file.
            node_index (int): index for the node in the config.json list.

        Returns:
            Conf: An instance of Conf with settings loaded from the JSON file.
        """
        with open(file_path, 'r') as json_file:
            config = json.load(json_file)
        
        conf_instance = cls()
        
        index_host = int(config["ComputingResources"]["index_host"])
        host_address = config["ComputingResources"]["nodes_ip"][index_host]
        
        conf_instance.mngt_outputdir = config["Basecalling"]["output_dir"]
        conf_instance.mngt_inputdir = config["Basecalling"]["input_dir"]

        if node_index != index_host:
            conf_instance.request_work_url = f'http://{host_address}:57967/assignwork'
        else:
            conf_instance.request_work_url = f'http://127.0.0.1:57967/assignwork'
        
        conf_instance.engine_external_script = config["Basecalling"]["supervisor_script_path"]
        conf_instance.engine_outputdir = config["Basecalling"]["output_dir"]
        conf_instance.engine_inputdir = config["Basecalling"]["input_dir"]
        conf_instance.engine_polling_interval = 1

        conf_instance.engine_id = config["ComputingResources"]["nodes_list"][node_index]
        conf_instance.engine_optimal_request_size = config["ComputingResources"]["batch_size_list"][node_index]

        conf_instance.engine_model = config["Basecalling"]["model"]
        
        if node_index != index_host:
            conf_instance.keep_alive_terminate_url = f'http://{host_address}:57967/completed'
            conf_instance.keep_alive_url = f'http://{host_address}:57967/keepalive'
        else:
            conf_instance.keep_alive_terminate_url = f'http://127.0.0.1:57967/completed'
            conf_instance.keep_alive_url = f'http://127.0.0.1:57967/keepalive'

        return conf_instance
