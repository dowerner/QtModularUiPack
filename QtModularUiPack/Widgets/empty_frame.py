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

from PyQt5.QtWidgets import QFrame, QMainWindow
from PyQt5.QtCore import pyqtSignal
from QtModularUiPack.Widgets.DataBinding.bindings import BindingEnabledWidget


class EmptyFrame(QFrame, BindingEnabledWidget):
    """
    The empty frame can be used as a place holder in a modular frame.
    This class serves as a base class for all tool frames which can be placed in a modular frame and use data binding.
    """
    name = 'empty frame'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def closing(self):
        pass

    @classmethod
    def standalone_application(cls, title=None, window_size=None, **kwargs):
        """
        Generates a standalone application from the widget.
        :param title: optional title for the application window. If no title is given the widget name will be taken
        :param window_size: size of window
        """
        if title is None:
            title = cls.name

        from PyQt5.Qt import QApplication

        app = QApplication([])
        main = StandaloneWindow()
        widget = cls(**kwargs)
        main.setCentralWidget(widget)
        main.setWindowTitle(title)
        main.on_closing.connect(widget.closing)

        if window_size is not None:
            width, height = window_size
            main.resize(int(width), int(height))

        main.show()
        QApplication.instance().exec_()

    def add_widget(self, widget, binding_variable_name=None, binding_attribute_setter=None, width=None, height=None, operation=None, inv_op=None):
        """
        This utility method will take a widget and set it up with a binding and sets its dimensions.
        :param widget: newly created widget
        :param binding_variable_name: variable in data context to bind to
        :param binding_attribute_setter: attribute of the widget the binding should update
        :param width: fixed width of the widget (no fixed width if None)
        :param height: fixed height of the widget (no fixed width if None)
        :return:
        """
        if binding_variable_name is not None and binding_attribute_setter is not None:
            self.bindings.set_binding(binding_variable_name, widget, binding_attribute_setter, operation=operation, inv_op=inv_op)

        if width is not None:
            widget.setFixedWidth(width)

        if height is not None:
            widget.setFixedHeight(height)

        return widget


class StandaloneWindow(QMainWindow):

    on_closing = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def closeEvent(self, *args, **kwargs):
        self.on_closing.emit()
        super().closeEvent(*args, **kwargs)

