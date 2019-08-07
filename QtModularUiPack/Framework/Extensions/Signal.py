class Signal(object):
    """
    A signal to fire events
    """

    def __init__(self, *types):
        self._types = types
        self._callbacks = list()

    def connect(self, callback):
        """
        Connect callback function to signal
        :param callback: callback function to execute on signal
        """
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
            if not isinstance(args[i], t):
                raise TypeError('Argument {} has the type "{}" but "{}" was expected.'.format(i, type(args[i]), t))

        for callback in self._callbacks:
            callback(*args)