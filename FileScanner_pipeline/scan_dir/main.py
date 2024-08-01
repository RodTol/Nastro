import sys
from create_samplesheet import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.pipelineInteract import Jenkins_trigger
# ANSI escape code for green text
GREEN = "\033[92m"
RESET = "\033[0m"
RED = "\033[91m"


if __name__ == "__main__":
    dir = sys.argv[1]
    model = sys.argv[2]
    output = sys.argv[3]
    samplesheet_not_found = False


    #Look for existing samplesheet
    existing_samplesheet = list_json(dir)
    if len(existing_samplesheet) == 0:
        print(f"I wasn't able to find any existing samplesheet inside {GREEN}{dir}{RESET}")
        #Create a new samplesheet
        samplesheet = Samplesheet(create_blank_samplesheet(dir, model))
        print("A {GREEN}new samplesheet was created{RESET}")
        update_samplesheet(samplesheet)
    else: 
        for sheet in existing_samplesheet:
            if is_same_samplesheet(sheet, dir, model):
                print(f"An EXISTING samplesheet for {GREEN}{model}{GREEN} was found inside {GREEN}{dir}{RESET}")
                samplesheet = Samplesheet(sheet)
                update_samplesheet(samplesheet)
                samplesheet_not_found = False
                break
            else:
                samplesheet_not_found = True

    if samplesheet_not_found :    
        #Create a new samplesheet
        samplesheet = Samplesheet(create_blank_samplesheet(dir, model))
        print(f"A {GREEN}new samplesheet{RESET} was created")
        update_samplesheet(samplesheet)

