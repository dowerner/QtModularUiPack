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

from QtModularUiPack.Framework import is_non_strict_type
from PyQt5.QtCore import QMetaObject, Q_ARG
from time import sleep
import h5py


class BaseExperiment(object):
    """
    Base class for all experiments
    """

    name = 'BaseExperiment'

    def __init__(self, tools, required_tools=None):
        self.required_tools = required_tools
        self.tools = tools
        self._validate_tools_()
        self.calling_context = None

    def save_h5(self, path, data, dataset='data'):
        """
        Save data as h5-binary file
        :param path: path to file
        :param data: data (numpy ndarray)
        :param dataset: name of dataset in which to save the data
        """
        hf = h5py.File(path, 'w')
        hf.create_dataset(dataset, data=data)
        hf.close()

    def run(self):
        """
        Run experiment
        """
        raise NotImplementedError()

    def message(self, message, title=None):
        """
        Displays a message box during experiment
        :param message: message
        :param title: title
        """
        if self.calling_context is not None:
            QMetaObject.invokeMethod(self.calling_context, 'message', Q_ARG(str, message), Q_ARG(str, title))
            self.calling_context.dialog_open = True
            self.wait_for_dialog()
        else:
            print(message)

    def question(self, message, title=None):
        """
        Displays a question dialog during the experiment (yes or no question)
        :param message: question
        :param title: title
        :return: true or false
        """
        if self.calling_context is not None:
            QMetaObject.invokeMethod(self.calling_context, 'question', Q_ARG(str, message), Q_ARG(str, title))
            self.calling_context.dialog_open = True
            self.wait_for_dialog()
            return self.calling_context.dialog_answer
        else:
            return bool(input(message))

    def wait_for_dialog(self):
        """
        Waits for dialog to close
        """
        if self.calling_context is not None:
            while self.calling_context.dialog_open:
                sleep(0.001)

    def _validate_tools_(self):
        """
        Check if the required tools are present in the Lab Master application
        """
        if self.required_tools is not None:
            for tool_type in self.required_tools:
                found = False
                for member in self.tools.__dict__:
                    tool = self.tools.__dict__[member]
                    if is_non_strict_type(type(tool), tool_type):
                        found = True
                        break
                if not found:
                    raise Exception('The required tool of type "{}" was not found.'.format(tool_type))
