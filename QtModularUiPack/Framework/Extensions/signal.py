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


class Signal(object):
    """
    A signal to fire events
    """

    def __init__(self, *types):
        self._types = types
        self._callbacks = list()

    def __del__(self):
        self._types = list()
        self._callbacks = list()

    def connect(self, callback):
        """
        Connect callback function to signal
        :param callback: callback function to execute on signal
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def disconnect(self, callback):
        """
        Disconnect callback function to signal
        :param callback: callback to disconnect from signal
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def emit(self, *args):
        """
        Emit signal to trigger callbacks
        :param args: arguments
        """
        if len(args) != len(self._types):
            raise Exception('Expected {} arguments but got {}.'.format(len(self._types), len(args)))

        for i in range(len(args)):
            t = self._types[i]
            if args[i] is not None and not isinstance(args[i], t):
                raise TypeError('Argument {} has the type "{}" but "{}" was expected.'.format(i, type(args[i]), t))

        for callback in self._callbacks:
            callback(*args)
