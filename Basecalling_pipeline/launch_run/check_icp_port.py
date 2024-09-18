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

import zmq
import sys
import os

def check_connection(ipc_file_path):
    # Check if the IPC file exists
    if not os.path.exists(ipc_file_path):
        print(f"Error: IPC file {ipc_file_path} does not exist.")
        return False

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    try:
        # Attempt to connect to the IPC endpoint
        socket.connect(ipc_file_path)
        print(f"Connected to IPC endpoint: {ipc_file_path}")
        return True
    except zmq.error.ZMQError as e:
        print(f"Error: Connection to IPC endpoint {ipc_file_path} failed - {e}")
        return False
    finally:
        # Properly close the socket and terminate the context
        socket.close()
        context.term()

if __name__ == "__main__":
    # Check the number of command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <ipc_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    connection_up = check_connection(file_path)

    if connection_up:
        print("True")
    else:
        print("False")
