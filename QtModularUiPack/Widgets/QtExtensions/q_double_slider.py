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

from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout
from PyQt5.QtCore import QSize, pyqtSignal, Qt


SLIDER_OFFSET = 10


class QDoubleSlider(QWidget):
    """
    This slider widget supports float values and non-integer incrementation
    """
    valueChanged = pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.setLayout(layout)

        # default setup
        self._maximum = 100
        self._minimum = 0
        self._increment = 1
        self._interval = 100
        self._steps = 100
        self._value = 0

        # add slider which will be wrapped
        self._slider = QSlider(Qt.Horizontal, *args, **kwargs)
        self._slider.setFixedSize(QSize(180, 20))   # default size
        self._slider.valueChanged.connect(self._slider_value_changed_)  # listen to value changes in the slider
        layout.addWidget(self._slider)
        self._setup_slider_()   # setup

    def _slider_value_changed_(self, value):
        """
        This method catches the changed signal of the wrapped slider and maps the integer values to the float space
        :param value: integer slider value
        """
        self._value = self._interval / self._steps * value + self._minimum  # transform to float space
        self.valueChanged.emit(self._value)     # emit value changed signal

    def sizeHint(self):
        """
        Needed for display
        """
        return QSize(200, 20)

    def _setup_slider_(self):
        """
        Configures the wrapped slider widget such that it can be used for the specified float values.
        """
        if self._maximum == 0:  # make sure there are no division by zero errors
            self._maximum = 1
        self._interval = self._maximum - self._minimum  # get the interval size in float space

        self._steps = int(self._interval / self._increment)     # get the required integer steps
        self._slider.setMaximum(self._steps)    # set the wrapped slider up with the correct number of steps

        # make sure the slider value is legal
        if self._value > self._maximum:
            self._value = self._maximum
        if self._value < self._minimum:
            self._value = self._minimum

        # convert the value from float to integer space and assign it to the wrapped slider
        adjusted_value = self._value - self._minimum
        slider_value = int(adjusted_value * self._steps / self._interval)
        self._slider.setValue(slider_value)

    def setIncrement(self, value):
        """
        Sets the incrementation of the slider.
        :param value: possibly non-integer incrementation
        """
        self._increment = value
        self._setup_slider_()

    def setValue(self, value):
        """
        Sets the value of the slider.
        :param value: possibly non-integer value
        """
        self._value = value
        self._setup_slider_()
        self.valueChanged.emit(value)

    def setMaximum(self, value):
        """
        Sets the maximum of the slider.
        :param value: possibly non-integer maximum
        """
        self._maximum = value
        self._setup_slider_()

    def setMinimum(self, value):
        """
        Sets the minimum of the slider.
        :param value: possibly non-integer minimum
        """
        self._minimum = value
        self._setup_slider_()

    def value(self):
        """
        Gets the value of the slider.
        """
        return self._value

    def maximum(self):
        """
        Gets the maximum of the slider.
        """
        return self._maximum

    def minimum(self):
        """
        Gets the minimum of the slider.
        """
        return self._minimum

    def setFixedSize(self, size):
        super().setFixedSize(size)
        n_size = QSize(size.width() - SLIDER_OFFSET, size.height())
        self._slider.setFixedSize(n_size)

    def setFixedHeight(self, p_int):
        super().setFixedHeight(p_int)
        self._slider.setFixedHeight(p_int)

    def setFixedWidth(self, p_int):
        super().setFixedWidth(p_int)
        self._slider.setFixedWidth(p_int)

