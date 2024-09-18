# Copyright 2024 Area Science Park
# Author: Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class mainParameters:
    def __init__(self, samplesheet, input_dir, output_dir, logs_dir, basecalling_model):
        self.samplesheet = samplesheet
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logs_dir = logs_dir
        self.basecalling_model = basecalling_model

    def __str__(self):
        return (f"mainParameters:\n"
                f"  Samplesheet: {self.samplesheet}\n"
                f"  Input Directory: {self.input_dir}\n"
                f"  Output Directory: {self.output_dir}\n"
                f"  Logs Directory: {self.logs_dir}\n"
                f"  Basecalling Model: {self.basecalling_model}")