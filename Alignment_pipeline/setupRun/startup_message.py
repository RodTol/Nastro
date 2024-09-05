import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_bar
from Basecalling_pipeline.monitor_run.bot_telegram import telegram_send_message

if __name__ == "__main__":
    dir = sys.argv[1]

    telegram_send_bar("-----ALIGNMENT-RUN-----")
    #TODO maybe add a time expectation
    message = f"""Merging the .fastq files from {dir}
"""
    telegram_send_bar(message)