from PyQt5.QtWidgets import QSlider, QStyle
from PyQt5.QtCore import pyqtSignal


class QJumpSlider(QSlider):
    """
    Slider that will jump to the position clicked instead of skipping
    """

    valueChangedSmart = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setValueSilent(self, value):
        super().setValue(value)

    def setValue(self, value):
        super().setValue(value)
        self.valueChangedSmart.emit(value)

    def mousePressEvent(self, event):
        # Jump to click position
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))

    def mouseMoveEvent(self, event):
        # Jump to pointer position while moving
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))