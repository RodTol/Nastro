import sys

sys.path.append("../subset_creation")
from runParameters import runParameters

if __name__ == "__main__":
    run_params = runParameters.from_file(sys.argv[1])