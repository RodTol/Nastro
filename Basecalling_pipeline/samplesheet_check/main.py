#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import sys
from samplesheet_api import Samplesheet


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py path/to/file.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    #TODO how to handle what to do if it fails
    samplesheet = Samplesheet(input_file)
