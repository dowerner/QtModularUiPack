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

from PyQt5.QtWidgets import QHBoxLayout
from QtModularUiPack.ViewModels import BaseContextAwareViewModel, ModularApplicationViewModel
from QtModularUiPack.Widgets import ModularFrameHost, EmptyFrame
from QtModularUiPack.Framework.ImportTools.utils import is_non_strict_type, is_non_strict_subclass
import os


class ModularApplication(EmptyFrame):
    """
    This is the main window of the Lab Master application
    """

    @property
    def frame_search_path(self):
        """
        Gets the path where the host looks for tool frames which can be displayed
        :return: path
        """
        return self._frame_host.frame_search_path

    @frame_search_path.setter
    def frame_search_path(self, value):
        """
        Sets the path where the host looks for tool frames which can eb displayed
        :param value: path
        """
        self._frame_host.frame_search_path = value

    def __init__(self, *args, frame_search_path=None, configuration_path=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_context = ModularApplicationViewModel()
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self.configuration_path = configuration_path
        self._save_file_locked = False

        # content
        self._frame_host = ModularFrameHost(self, frame_search_path=frame_search_path)
        self._frame_host.data_context_received.connect(self._on_child_data_context_received_)
        self._frame_host.data_context_removed.connect(self._on_child_data_context_removed_)
        self._layout.addWidget(self._frame_host)

        if configuration_path is not None:
            self.load_settings(configuration_path)

    @classmethod
    def standalone_application(cls, title=None, window_size=None, frame_search_path=None, configuration_path=None):
        """
        Launch modular standalone application
        :param title: Application title
        :param window_size: initial window size
        :param frame_search_path: path to look for application frames
        :param configuration_path: path to save application state to (expected json file)
        """
        super().standalone_application(title, window_size,
                                       frame_search_path=frame_search_path,
                                       configuration_path=configuration_path)

    def _on_child_data_context_received_(self, child_data_context):
        """
        Callback for handling new data contexts that have been added in the tool frame section
        :param child_data_context: data context that was added
        :return:
        """
        if child_data_context not in self.data_context.other_data_contexts:
            self.data_context.other_data_contexts.append(child_data_context)

        if is_non_strict_subclass(type(child_data_context), BaseContextAwareViewModel):
            self.data_context.connect_context_aware_view_model(child_data_context)

        self.save()

    def _on_child_data_context_removed_(self, child_data_context):
        """
        Callback for handling new data contexts that have been removed in the tool frame section
        :param child_data_context: data context that was removed
        :return:
        """
        if child_data_context in self.data_context.other_data_contexts:
            self.data_context.other_data_contexts.remove(child_data_context)

        if is_non_strict_type(type(child_data_context), BaseContextAwareViewModel):
            self.data_context.disconnect_context_aware_view_model(child_data_context)

        self.save()

    def load_settings(self, path):
        """
        Load settings of frames
        :param path: path where to load the settings from
        """
        if os.path.isfile(path):
            self._save_file_locked = True
            self._frame_host.load(path)
            self._save_file_locked = False

    def save(self):
        if self.configuration_path is not None and not self._save_file_locked and not self._frame_host.is_restoring:
            self._save_file_locked = True
            self._frame_host.save(self.configuration_path)
            self._save_file_locked = False

    def closing(self):
        self.save()
        self.data_context.save_configuration()   # save configuration on close
