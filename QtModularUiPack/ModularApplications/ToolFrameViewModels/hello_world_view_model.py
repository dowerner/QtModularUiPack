from ViewModels import BaseViewModel


class HelloWorldViewModel(BaseViewModel):

    name = 'hello_world'

    @property
    def upper_text(self):
        return self._upper_text

    @upper_text.setter
    def upper_text(self, value):
        self._upper_text = value
        self.notify_change('upper_text')

    @property
    def lower_text(self):
        return self._lower_text

    @lower_text.setter
    def lower_text(self, value):
        self._lower_text = value
        self.notify_change('lower_text')

    def __init__(self):
        super().__init__()
        self._upper_text = 'Hello World!'
        self._lower_text = 'Goodbye'

    def switch(self):
        temp = self.upper_text
        self.upper_text = self.lower_text
        self.lower_text = temp
