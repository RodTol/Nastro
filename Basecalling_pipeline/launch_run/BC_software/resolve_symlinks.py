# Copyright 2024 Rodolfo Tolloi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

def get_real_path(path):
    if os.path.islink(path):
        real_path = os.path.realpath(path)
        return real_path
    else:
        return path

def resolve_symlinks(directory):
    real_paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            real_paths.append(get_real_path(filepath))

    return real_paths

