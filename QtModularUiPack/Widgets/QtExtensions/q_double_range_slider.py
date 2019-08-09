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

from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSizePolicy
from QtModularUiPack.Widgets.QtExtensions import QRangeSlider


CONTROL_OFFSET = 10


class QDoubleRangeSlider(QWidget):
    """
    This range slider supports non-integer values and increments.
    """
    minValueChanged = pyqtSignal(float)
    maxValueChanged = pyqtSignal(float)
    startValueChanged = pyqtSignal(float)
    endValueChanged = pyqtSignal(float)
    incrementChanged = pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # make the widget use as much space as possible
        layout = QHBoxLayout()
        self.setLayout(layout)

        # initialize it like the standard slider
        self._minimum = 0
        self._maximum = 100
        self._start = 0
        self._end = 0
        self._increment = 1
        self._interval = 100
        self._steps = 100

        # initialize the slider which is going to be wrapped
        self._slider = QRangeSlider(*args, **kwargs)
        self._slider.setFixedSize(QSize(100, 30))   # standard-size when initialized
        self._slider.startValueChanged.connect(self._slider_start_value_changed_)   # listen to slider changes
        self._slider.endValueChanged.connect(self._slider_end_value_changed_)       # listen to slider changes
        self._slider.setDrawValues(False)   # don't draw values (They would be wrong because of the wrapping technique)
        layout.addWidget(self._slider)
        self._handle_slider_()      # set slider values

    def setFixedSize(self, size):
        """
        Set size of the slider
        :param size: QSize
        """
        super().setFixedSize(size)  # set widget size
        n_size = QSize(size.width() - CONTROL_OFFSET, size.height())    # size of the wrapped slider with offset
        self._slider.setFixedSize(n_size)   # set size on the wrapped slider

    def setFixedWidth(self, p_int):
        """
        Set width of the slider
        :param p_int: width
        """
        super().setFixedWidth(p_int)
        self._slider.setFixedWidth(p_int - CONTROL_OFFSET)  # set width with offset

    def setFixedHeight(self, p_int):
        """
        Set height of the slider
        :param p_int: height
        """
        super().setFixedHeight(p_int)
        self._slider.setFixedHeight(p_int)

    def sizeHint(self):
        return QSize(200, 200)

    def _slider_start_value_changed_(self, int_value):
        """
        Catch signals of the wrapped slider and process the new values
        :param int_value: new start value
        """
        self._start = self._interval / self._steps * int_value + self._minimum  # convert from integer to float space
        self.startValueChanged.emit(self._start)    # emit signal

    def _slider_end_value_changed_(self, int_value):
        """
        Catch signals of the wrapped slider and process the new values
        :param int_value: new end value
        """
        self._end = self._interval / self._steps * int_value + self._minimum    # convert from integer to float space
        self.endValueChanged.emit(self._end)    # emit signal

    def _handle_slider_(self):
        """
        Configures the wrapped slider widget such that it can be used for the specified float values.
        """
        if self._maximum == 0:  # make sure there is no zero division
            self._maximum = 1
        self._interval = self._maximum - self._minimum  # get the interval covered in float space

        self._steps = int(self._interval / self._increment)     # get the steps required in integer space
        self._slider.setMax(self._steps)    # make sure the wrapped slider has enough steps

        # make sure the start and end values are legal
        if self._end > self._maximum:
            self._end = self._maximum
        if self._start < self._minimum:
            self._start = self._minimum
        if self._end < self._start:
            self._end = self._start
        if self._start > self._end:
            self._start = self._end

        # transform the start and end values from float to integer space and set them on the wrapped slider
        adjusted_start = self._start - self._minimum
        adjusted_end = self._end - self._minimum

        start_value = int(adjusted_start * self._steps / self._interval)
        end_value = int(adjusted_end * self._steps / self._interval)

        self._slider.setStart(start_value)
        self._slider.setEnd(end_value)

    def setIncrement(self, value):
        """
        Sets the incrementation of the slider.
        :param value: possibly non-integer incrementation
        """
        self._increment = value
        self._handle_slider_()
        self.incrementChanged.emit(value)

    def setMax(self, value):
        """
        Sets the maximum of the slider.
        :param value: possibly non-integer maximum
        """
        self._maximum = value
        self._handle_slider_()
        self.maxValueChanged.emit(value)

    def setMin(self, value):
        """
        Sets the minimum of the slider.
        :param value: possibly non-integer minimum
        """
        self._minimum = value
        self._handle_slider_()
        self.minValueChanged.emit(value)

    def setStart(self, value):
        """
        Sets the start of the slider.
        :param value: possibly non-integer start
        """
        self._start = value
        self._handle_slider_()
        self.startValueChanged.emit(value)

    def setEnd(self, value):
        """
        Sets the end of the slider.
        :param value: possibly non-integer end
        """
        self._end = value
        self._handle_slider_()
        self.endValueChanged.emit(value)

    def setRange(self, start, end):
        """
        Sets the range of the slider.
        :param start: possibly non-integer start
        :param end: possibly non-integer end
        :return:
        """
        self.setStart(start)
        self.setEnd(end)

    def min(self):
        """
        Gets the minimum of the slider.
        """
        return self._minimum

    def max(self):
        """
        Gets the maximum of the slider.
        """
        return self._maximum

    def start(self):
        """
        Gets the start value of the slider.
        """
        return self._start

    def end(self):
        """
        Gets the end value of the slider.
        """
        return self._end
