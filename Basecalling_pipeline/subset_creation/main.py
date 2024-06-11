import sys
from subset_creator import Subsetter

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py path/to/file.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    subsetter = Subsetter(input_file)

    batch = subsetter.create_batch()

