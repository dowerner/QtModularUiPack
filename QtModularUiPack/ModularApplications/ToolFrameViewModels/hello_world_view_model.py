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

from QtModularUiPack.ViewModels import BaseViewModel


class HelloWorldViewModel(BaseViewModel):
    """
    This is a simple example on how to implement a modular frame that can be integrated into the architecture of
    QtModularUiPack-Applications.

    This examples comprises the files: hello_world_frame.py, hello_world_view_model.py
    """

    name = 'hello_world'

    @property
    def upper_text(self):
        """
        Gets text in upper text box
        """
        return self._upper_text

    @upper_text.setter
    def upper_text(self, value):
        """
        Sets text in upper text box
        :param value: text
        """
        self._upper_text = value
        self.notify_change('upper_text')

    @property
    def lower_text(self):
        """
        Gets text in lower text box
        """
        return self._lower_text

    @lower_text.setter
    def lower_text(self, value):
        """
        Sets text in lower text box
        :param value: text
        """
        self._lower_text = value
        self.notify_change('lower_text')

    def __init__(self):
        super().__init__()
        self._upper_text = 'Hello World!'
        self._lower_text = 'Goodbye'

    def switch(self):
        """
        Switches texts in upper and lower text boxes (serves to illustrate data-binding)
        """
        temp = self.upper_text
        self.upper_text = self.lower_text
        self.lower_text = temp
