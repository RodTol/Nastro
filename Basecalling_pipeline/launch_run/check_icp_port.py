#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

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
