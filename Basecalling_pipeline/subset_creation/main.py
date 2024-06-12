import sys
import hashlib
import datetime

from subset_creator import Subsetter


def generate_short_hash(input_str):
    return hashlib.sha256(input_str.encode()).hexdigest()[:8]

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 main.py path/to/file.json path/to/output/root/dir path/to/logs/root/dir basecalling model")
        sys.exit(1)
    
    #Create batch hash identifier
    time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    run_id = generate_short_hash(time)

    #Create subset
    input_file = sys.argv[1]
    subsetter = Subsetter(input_file)
    run_samplesheet = subsetter.create_subset()

    print(run_id)
    #Create batch personal directories for input, output and logs

