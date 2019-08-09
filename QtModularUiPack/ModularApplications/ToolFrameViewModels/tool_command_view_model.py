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

from QtModularUiPack.ViewModels import BaseContextAwareViewModel
import traceback
import sys
import io
import threading


class ToolCommandViewModel(BaseContextAwareViewModel):
    """
    This is the data-context for the integrate python console frame.
    If this data context is used within a modular application it can access all other data-contexts present
    """

    name = 'console'

    @property
    def command_index(self):
        """
        Gets the current command index
        """
        return self._command_index

    @command_index.setter
    def command_index(self, value):
        """
        Sets the current command index (this changes the command in the command line)
        """
        if len(self.commands) > value >= 0:
            self._command_index = value
            self.command = self.commands[value]
            self.notify_change('command')
            self.notify_change('command_index')

    @property
    def command(self):
        """
        Gets the current command
        """
        return self._command

    @command.setter
    def command(self, value):
        """
        Sets the current command
        """
        self._command = value

    @property
    def console_content(self):
        """
        Gets the console content
        """
        return self._console_content

    @console_content.setter
    def console_content(self, value):
        """
        Sets the console content
        """
        self._console_content = value
        self.notify_change('console_content')

    def __init__(self):
        super().__init__()
        self.commands = [None]
        self._command_index = 0
        self._command = None
        self._console_content = ''
        self._tool_frame_data_contexts = None
        self._console_context = dict()
        self._stdin_backup = sys.stdin      # create backup of standard input
        self._stdout_backup = sys.stdout    # create backup of standard output
        self._stderr_backup = sys.stderr    # create backup of standard error output
        self._console_input = ConsoleWrapper(io.BytesIO())
        self._console_output = ConsoleWrapper(io.BytesIO())
        self._console_error = ConsoleWrapper(io.BytesIO())
        self._console_input.changed.append(self._on_stdout_changed_)
        self._console_output.changed.append(self._on_stdout_changed_)
        self._console_error.changed.append(self._on_stdout_changed_)
        self._ui_thread = threading.current_thread()
        self._off_thread_console_content = list()
        self.start_commands = ['import numpy as np', '# type "tools.help()" to see the tools you have currently access to.']

        # initialize tools
        self._tools = self.data_context_container

        # run start commands
        for command in self.start_commands:
            self.command = command
            self.run_command()

    def run_command(self):
        """
        Run command currently typed into command line
        """
        if self.command is None:
            return
        try:
            # create local clear function
            def clear():
                self.console_content = ''

            # set standard output to console
            sys.stdin = self._console_input
            sys.stdout = self._console_output
            sys.stderr = self._console_error

            # load local variables
            tools = self._tools
            local_variables = locals()
            for local in self._console_context:
                if local != 'self' and local != 'tools' and local != 'local_variables':
                    local_variables[local] = self._console_context[local]

            # run code
            self.console_content += self.command + '\n'
            if '=' not in self.command and ' ' not in self.command:
                exec('out = {}'.format(self.command))
                if 'out' in local_variables and local_variables['out'] is not None:
                    print('[out]: {}'.format(local_variables['out']))
            else:
                exec(self.command)

            # store created variables global
            for local in list(local_variables.keys()):
                if local != 'self' and local != 'tools' and local != 'local_variables':
                    self._console_context[local] = local_variables[local]
        except Exception as e:
            traceback.print_exc()
            print('Error during command execution, Error: {}'.format(e))
        finally:
            self.commands.insert(len(self.commands) - 1, self.command)
            self.command_index = len(self.commands) - 1

            sys.stdin = self._stdin_backup
            sys.stdout = self._stdout_backup
            sys.stderr = self._stderr_backup

    def _on_stdout_changed_(self, s):
        if self._ui_thread == threading.current_thread():   # make sure only data from the main thread gets sent to console
            self.console_content += s
        else:  # send data from other threads to the standard python console
            sys.stdout = self._stdout_backup
            sys.stdout.write(s)
            sys.stdout = self._console_output


class ConsoleWrapper(io.TextIOWrapper):
    """
    Text IO Wrapper that can alert write changes
    """

    def write(self, s: str):
        super().write(s)
        for callback in self.changed:
            callback(s)

    def __init__(self, *args):
        super().__init__(*args)
        self.changed = list()
