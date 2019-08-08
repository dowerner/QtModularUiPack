from Framework import Signal


class BaseViewModel(object):
    """
    This is the base view model class to be implemented by all data context classes
    """

    name = 'data_context'

    property_changed = Signal(str)

    def __init__(self):
        pass

    def notify_change(self, name):
        """
        Send notification that a variable has been changed that the binding enabled widgets can update accordingly
        :param name: variable name
        """
        self.property_changed.emit(name)
