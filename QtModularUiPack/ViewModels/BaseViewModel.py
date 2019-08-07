class BaseViewModel(object):
    """
    This is the base view model class to be implemented by all data context classes
    """

    name = 'data_context'

    def __init__(self):
        self.property_changed = list()

    def notify_change(self, name):
        """
        Send notification that a variable has been changed that the binding enabled widgets can update accordingly
        :param name: variable name
        """
        for callback in self.property_changed:
            callback(name)
