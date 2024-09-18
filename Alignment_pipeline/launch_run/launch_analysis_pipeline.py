#__author__      ="Rodolfo Tolloi"
#__subject__     ="Nastro Pipeline"
#__tags__        ="Bioinformatics, Nanopore, Dorado"
#__copyright__   ="Copyright 2021, AREA SCIENCE PARK - RIT"
#__credits__     =
#__license__     ="Apache License 2.0"
#__version__     =
#__maintainer__  =
#__status__      ="Development"

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.subset_creation.pipelineInteract import Jenkins_trigger

if __name__ == "__main__":
    jenkins_parameter =  {
        "pathToSamplesheet": sys.argv[1],
        "RunId": sys.argv[2]
    }

    jenkins = Jenkins_trigger()
    jenkins.start_job('tolloi/Pipeline_long_reads/analysis_pipeline', 'manwe', jenkins_parameter)
