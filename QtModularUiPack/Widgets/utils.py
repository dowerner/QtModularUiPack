"""
Copyright 2019 Dominik Werner

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from QtModularUiPack.ModularApplications import *
from QtModularUiPack.Framework import is_non_strict_subclass
from QtModularUiPack.Widgets import EmptyFrame


def get_builtin_frames():
    """
    Get a list of all built-in frames complatible for the use in a modular frame application
    :return: list of classes derived form EmptyFrame
    """
    glob = globals()
    builtin_frames = [EmptyFrame]
    for member in glob:
        if glob[member] not in builtin_frames and is_non_strict_subclass(glob[member], EmptyFrame):
            builtin_frames.append(glob[member])
    return builtin_frames

