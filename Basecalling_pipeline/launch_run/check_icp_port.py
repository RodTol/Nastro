import zmq
import os
import sys

def check_connection(ipc_file_path):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    try:
        socket.connect(ipc_file_path)
        print(f"Connected to IPC endpoint: {ipc_file_path}")
        return True
    except zmq.error.ZMQError as e:
        print(f"Error: Connection to IPC endpoint {ipc_file_path} failed - {e}")
        return False
    finally:
        socket.close()
        context.term()

file_path = sys.argv[1]
connection_up = check_connection(file_path)

if connection_up:
    print("True")
else:
    print("False")
