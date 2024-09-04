import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet


if __name__ == "__main__":
    samplehseet = Samplesheet(sys.argv[1])
    id = sys.argv[2]
    status = sys.argv[3]

    for file in samplehseet.get_files:
        if file["aligned"] == id:
            file["aligned"] = status
    
    samplehseet.update_json_file()