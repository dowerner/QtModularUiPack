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

from QtModularUiPack.Widgets import EmptyFrame
from PyQt5.QtWidgets import QLineEdit, QPushButton, QGridLayout
from QtModularUiPack.ModularApplications.ToolFrameViewModels.hello_world_view_model import HelloWorldViewModel


class HelloWorldFrame(EmptyFrame):
    """
    This is a simple example on how to implement a modular frame that can be integrated into the architecture of
    QtModularUiPack-Applications.

    This examples comprises the files: hello_world_frame.py, hello_world_view_model.py
    """

    name = 'Hello World Frame'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = HelloWorldViewModel()   # add data context which provides the data and handles updates
        self._layout = QGridLayout()    # add grid layout
        self.setLayout(self._layout)    # set layout to frame
        self._setup_()  # setup UI

    def _setup_(self):
        upper_box = QLineEdit('Hello World')
        lower_box = QLineEdit('Goodbye')
        switch_button = QPushButton('switch')

        self.bindings.set_binding('upper_text', upper_box, 'setText')
        self.bindings.set_binding('lower_text', lower_box, 'setText')
        switch_button.clicked.connect(self.data_context.switch)

        self._layout.addWidget(upper_box, 0, 0)
        self._layout.addWidget(lower_box, 1, 0)
        self._layout.addWidget(switch_button, 1, 1)
