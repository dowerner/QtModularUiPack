from QtModularUiPack.Widgets import EmptyFrame
from PyQt5.QtWidgets import QLineEdit, QPushButton, QGridLayout
from QtModularUiPack.ModularApplications.ToolFrameViewModels.hello_world_view_model import HelloWorldViewModel


class HelloWorldFrame(EmptyFrame):

    name = 'Hello World Frame'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = HelloWorldViewModel()
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self._setup_()

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
