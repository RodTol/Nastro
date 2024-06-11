import sys
from samplesheet_api import Samplesheet


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py path/to/file.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    samplesheet = Samplesheet(input_file)
