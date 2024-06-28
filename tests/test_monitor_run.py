from Basecalling_pipeline.monitor_run.bot_telegram import *
from Basecalling_pipeline.subset_creation.runParameters import runParameters


def test_message():
    params = runParameters.from_file('tests/test_files/test_run_params.json')
    telegram_send_message(f"Run_id: {params.id}")    
