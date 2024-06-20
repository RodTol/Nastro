import sys

sys.path.append("../subset_creation")
from runParameters import runParameters

if __name__ == "__main__":
    print("launch stage:", sys.argv[1])
    #run_params = runParameters.from_file(sys.argv[1])