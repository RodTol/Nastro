import os
import sys
import shutil
import subprocess


def check_Renamefiles_in_directory(dir_path):
    # List all files in the directory
    files_in_dir = os.listdir(dir_path)
    
    # Check for the specific files
    #TODO are this ok ? Maybe useful something connected to the run
    basecalling_file = 'BasecallingResults.fastq'
    alignment_file = 'AlignmentResults.bam'
    
    has_basecalling = basecalling_file in files_in_dir
    has_alignment = alignment_file in files_in_dir
    
    return has_basecalling and has_alignment

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.samplesheet_check.samplesheet_api import Samplesheet
if __name__ == "__main__":
    samplesheet = Samplesheet(sys.argv[1])
    id = sys.argv[2]


    output_dir = samplesheet.get_metadata()["outputLocation"]  
    pathToFinalBasecalling = f'{output_dir}/BasecallingResults.fastq'
    pathToFinalAlignment = f'{output_dir}/AlignmentResults.bam'

    #Check if there's already a .fastq or .bam merged file
    #TODO DO i live the path like this ?
    if check_Renamefiles_in_directory(output_dir):
        print("Results file are already present!")

        cat_command = f"cat {output_dir}/output/{id}/run_{id}_merged.fastq {pathToFinalBasecalling} > {pathToFinalBasecalling}"
        samtools_command = f"samtools merge -o {pathToFinalAlignment} {pathToFinalAlignment} {output_dir}/output/{id}/bam/run_{id}.bam"

        try:
            cat_process = subprocess.run(f"{cat_command}",
                                     shell=True, check=True, capture_output=True)
            print("Cat output:", cat_process.stdout)

            samtools_process = subprocess.run(f"{samtools_command}",
                                     shell=True, check=True, capture_output=True)
            print("Samtools output:", samtools_process.stdout)            

        except subprocess.CalledProcessError as e:
            print(f"Error executing commands: {e}")

    else:
        print("First time creating Results file")
        shutil.move(f'{output_dir}/output/{id}/run_{id}_merged.fastq', pathToFinalBasecalling)
        shutil.move(f'{output_dir}/output/{id}/bam/run_{id}.bam', pathToFinalAlignment)
