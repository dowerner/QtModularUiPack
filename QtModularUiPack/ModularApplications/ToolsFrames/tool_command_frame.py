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
from QtModularUiPack.ModularApplications.ToolFrameViewModels.tool_command_view_model import ToolCommandViewModel
from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui


class ToolCommandFrame(EmptyFrame):
    """
    This frame is a python console that allows direct access to all loaded frames in the application

    in the console:
      > tools.help()
    will display a list of available tools to control
    """

    name = 'Tool Command Line'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = ToolCommandViewModel()
        self._console = None
        self._layout = QVBoxLayout(self)
        self.setLayout(self._layout)
        self._setup_()

    def _get_last_command_(self):
        """
        Callback to navigate to previous commands
        :return:
        """
        self.data_context.command_index -= 1

    def _get_next_command_(self):
        """
        Callback to navigate to more recent commands
        :return:
        """
        self.data_context.command_index += 1

    def _scroll_to_end_(self):
        """
        Callback to scroll to the end of the console
        """
        if self._console is not None:
            try:
                self._console.moveCursor(QtGui.QTextCursor.End)
            except Exception as e:
                print(e)

    def _setup_(self):
        """
        Generate UI
        """

        # console
        self._layout.addWidget(QLabel('Tool Command Line'))
        self._console = self.add_widget(QTextEdit(), 'console_content', 'setText')
        self._console.textChanged.connect(self._scroll_to_end_)
        self._console.setReadOnly(True)
        self._layout.addWidget(self._console)

        # command line
        h_layout = QHBoxLayout(self)
        h_frame = QFrame(self)
        h_frame.setLayout(h_layout)
        self._layout.addWidget(h_frame)
        h_layout.addWidget(self.add_widget(QLabel(), width=20))

        input_line = self.add_widget(CommandLineEdit(), 'command', 'setText')
        input_line.returnPressed.connect(self.data_context.run_command)
        input_line.key_up_pressed.append(self._get_last_command_)
        input_line.key_down_pressed.append(self._get_next_command_)
        h_layout.addWidget(input_line)

        run_button = QPushButton('execute')
        run_button.clicked.connect(self.data_context.run_command)
        h_layout.addWidget(run_button)


class CommandLineEdit(QLineEdit):
    """
    This command line widget is a line edit widget that can also notify about up and down key press events
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.key_up_pressed = list()    # event for up key press
        self.key_down_pressed = list()  # event for down key press

    def event(self, event):
        """
        Makes sure that events are propagated correctly
        :param event: event
        """
        super().event(event)
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Up:
                for callback in self.key_up_pressed:
                    callback()
            elif event.key() == QtCore.Qt.Key_Down:
                for callback in self.key_down_pressed:
                    callback()
        return True
