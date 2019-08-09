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

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from pyqtgraph import ColorMap
from matplotlib.pyplot import get_cmap
import pyqtgraph as pg
import numpy as np

pg.setConfigOptions(antialias=True)


PY_GRAPH_PLOT_MODE_LINE = 'PLOT_MODE_LINE'
PY_GRAPH_PLOT_MODE_IMAGE = 'PLOT_MODE_IMAGE'


class PyGraphWidget(QFrame):
    """
    A very simple, one-plot plot widget based on PyQtGraph (faster for displaying large amounts of data than matplotlib)
    """

    x_position_indicator_changed = pyqtSignal(float)

    @property
    def title(self):
        """
        Gets the title of the plot
        """
        return self._title

    @title.setter
    def title(self, value):
        """
        Sets the title of the plot
        """
        self._title = value
        self._plot.setTitle(value, color=self._to_html_color_(self._title_color))

    @property
    def x_label(self):
        """
        Gets the x label of the plot
        """
        self._x_label

    @x_label.setter
    def x_label(self, value):
        """
        Sets the x label of the plot
        """
        self._set_x_axis_(value)

    @property
    def y_label(self):
        """
        Gets the y label of the plot
        :return:
        """
        return self._y_label

    @y_label.setter
    def y_label(self, value):
        """
        Sets the y label of the plot
        """
        self._set_y_axis_(value)

    @property
    def show_x_position_indicator(self):
        """
        Gets whether the x axis position indicator is shown
        """
        return self._show_x_position_indicator

    @show_x_position_indicator.setter
    def show_x_position_indicator(self, value):
        """
        Sets whether the x axis position indicator is shown
        :param value: True or false
        """
        self._show_x_position_indicator = value
        self._set_x_position_indicator_()

    @property
    def x_indicator_movable(self):
        """
        Gets whether the x axis position indicator can be moved by mouse
        """
        return self._x_indicator_movable

    @x_indicator_movable.setter
    def x_indicator_movable(self, value):
        """
        Sets whether the x axis position indicator can be moved by mouse
        :param value: True or false
        """
        self._x_indicator_movable = value
        self._set_x_position_indicator_()

    @property
    def x_indicator_color(self):
        """
        Gets the color of the x-position indicator
        """
        return self._x_indicator_color

    @x_indicator_color.setter
    def x_indicator_color(self, value):
        """
        Sets the color of the x-position indicator
        :param value: color
        """
        self._x_indicator_color = value
        self._set_x_position_indicator_()

    @property
    def x_indicator_text_color(self):
        """
        Gets the text color of the x-position indicator
        """
        return self._x_indicator_text_color

    @x_indicator_text_color.setter
    def x_indicator_text_color(self, value):
        """
        Sets the color of the x-position indicator
        :param value: color
        """
        self._x_indicator_text_color = value
        self._set_x_position_indicator_()

    @property
    def x_indicator_label(self):
        """
        Gets the text of the label on the x-position indicator
        """
        return self._x_indicator_label

    @x_indicator_label.setter
    def x_indicator_label(self, value):
        """
        Sets the text of the label on the x-position indicator
        :param value: text
        """
        self._x_indicator_label = value
        self._set_x_position_indicator_()

    @property
    def x_indicator_position(self):
        """
        Gets the position of the x-position indicator
        """
        return self._x_indicator_position

    @x_indicator_position.setter
    def x_indicator_position(self, value):
        """
        Sets the position of the x-position indicator
        :param value: position
        """
        self._x_indicator_position = value
        self._set_x_position_indicator_()

    def __init__(self, title=None, x_label=None, y_label=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)
        self._plot = pg.PlotWidget()
        self._image_item = pg.ImageItem()
        self._current_mode = None
        self._line_data = None
        self._line_color = 'w'
        self._background_color = 'k'
        self.set_background_color(self._background_color)
        self._layout.addWidget(self._plot)
        self._title = title
        self._x_label = x_label
        self._x_axis_color = QColor(150, 150, 150)
        self._y_label = y_label
        self._y_axis_color = QColor(150, 150, 150)
        self._show_x_position_indicator = False
        self._x_position_indicator = None
        self._x_indicator_movable = True
        self._x_indicator_text_color = Qt.red
        self._x_indicator_color = Qt.red
        self._x_indicator_label = 'x'
        self._x_indicator_position = 0
        self._show_fft = False
        self._fft_window = None
        self._title_color = QColor(150, 150, 150)
        self.title = title
        self._set_x_axis_(x_label)
        self._set_y_axis_(y_label)

    def set_matplotlib_default_style(self):
        """
        Tell the plot widget to mimic the default style of matplotlib's plots
        """
        self.set_indicator_colors(Qt.black)
        self.set_background_color(Qt.white)
        self.set_plot_color(QColor(31, 119, 180))   # matplotlib default blue

    def set_indicator_colors(self, color):
        """
        Sets the colors of the axes as well as the title
        :param color: color
        """
        self.set_title_color(color)
        self.set_x_axis_color(color)
        self.set_y_axis_color(color)

    def set_axes_color(self, color):
        """
        Sets the colors of both axes
        :param color: color
        """
        self.set_x_axis_color(color)
        self.set_y_axis_color(color)

    def set_x_axis_color(self, color):
        """
        Sets the color of the x axis
        :param color: color
        """
        self._x_axis_color = color
        self._set_x_axis_(self._x_label)

    def set_y_axis_color(self, color):
        """
        Sets the color of the y axis
        :param color: color
        """
        self._y_axis_color = color
        self._set_y_axis_(self._y_label)

    def set_title_color(self, color):
        """
        Sets the color of the title
        :param color: color
        """
        self._title_color = color
        self.title = self._title

    def set_plot_color(self, color):
        """
        Sets the color of the plot
        :param color: color of the plot
        """
        self._line_color = color
        if self._line_data is not None:
            self._line_data.setPen(self._line_color)

    @staticmethod
    def _to_valid_rgb_(color):
        """
        Converts a given color to an RGB value
        :param color: color
        :return RGB values
        """
        if type(color) == int or type(color) == Qt.GlobalColor:
            q_color = QColor(color)
            return q_color.red(), q_color.green(), q_color.blue()
        else:
            return color

    @staticmethod
    def _to_html_color_(color):
        """
        Converts a given color to a string in the HTML color format
        :param color: color
        :return: HTML color string
        """
        if type(color) != QColor:
            q_color = QColor(color)
        else:
            q_color = color
        return '#{0:02x}{1:02x}{2:02x}'.format(q_color.red(), q_color.green(), q_color.blue())

    def set_background_color(self, color):
        """
        Sets the background color
        :param color: color
        """
        self._background_color = self._to_valid_rgb_(color)
        pg.setConfigOption('background', self._background_color)
        self._plot.setBackground(self._background_color)
        self.update()

    def set_imshow(self, image_data, extent=None, c_map=None, auto_fit_plot=True):
        """
        Show 2D data on the plot.
        :param image_data: 2D array consisting of z-values
        :param extent: the range on the x and y axis that the data covers
        :param c_map: the colormap for the data, matplotlib's "viridis" is used if nothing is specified
        :param auto_fit_plot: if set to true will change the view to fit the data
        """
        if self._current_mode == PY_GRAPH_PLOT_MODE_LINE:
            self._plot.removeItem(self._line_data)
            self._line_data = None

        self._current_mode = PY_GRAPH_PLOT_MODE_IMAGE
        scale = (1, 1)
        offset = (0, 0)
        if extent is not None:
            x0 = extent[0]
            x1 = extent[1]
            y0 = extent[2]
            y1 = extent[3]
            width = x1 - x0
            height = y1 - y0
            scale = (width / image_data.shape[1], height / image_data.shape[0])
            offset = (x0, y0)
        if c_map is None:
            c_map = pyqtgraph_color_map_from_matplotlib('viridis')

        self._image_item.resetTransform()
        self._image_item.setImage(image_data.transpose())
        self._image_item.scale(*scale)
        self._image_item.setPos(*offset)
        self._image_item.setLookupTable(c_map.getLookupTable())
        self._plot.addItem(self._image_item)

        # move indicator to foreground
        if self._x_position_indicator is not None:
            self._plot.removeItem(self._x_position_indicator)
            self._plot.addItem(self._x_position_indicator)

        if auto_fit_plot:
            self._plot.enableAutoRange()
            self._plot.disableAutoRange()

    def set_data(self, x, y, auto_fit_plot=True):
        """
        Sets the x and y data of the plot
        :param x: x axis data
        :param y: y axis data
        :param auto_fit_plot: if set to true will change the view to fit the data
        """
        if self._current_mode == PY_GRAPH_PLOT_MODE_IMAGE:
            self._plot.removeItem(self._image_item)

        self._current_mode = PY_GRAPH_PLOT_MODE_LINE
        if self._line_data is None:
            self._line_data = PyGraphCustomPlotDataItem(x, y)
            self._line_data.fft_created.append(self._fft_created_)
            self._line_data.close_fft_window.append(self._close_fft_window_)
            self._plot.addItem(self._line_data)
            self._line_data.setPen(self._line_color)
        else:
            if len(x) < 2:
                self._plot.setDownsampling(auto=False)
            self._plot.getPlotItem().axes.clear()
            self._line_data.setData(x, y)

        # move indicator to foreground
        if self._x_position_indicator is not None:
            self._plot.removeItem(self._x_position_indicator)
            self._plot.addItem(self._x_position_indicator)

        self._plot.setClipToView(clip=False)
        if auto_fit_plot:
            self._plot.enableAutoRange()
            self._plot.disableAutoRange()
        if len(x) > 1:
            self._plot.setDownsampling(auto=True)

    def _set_x_position_indicator_(self):
        """
        Apply all settings to x-position indicator
        """
        if self._plot is None:
            return

        if not self._show_x_position_indicator and self._x_position_indicator is not None:
            self._plot.removeItem(self._x_position_indicator)
            self._x_position_indicator = None
            return

        if self._show_x_position_indicator and self._x_position_indicator is None:
            self._x_position_indicator = pg.InfiniteLine(movable=self._x_indicator_movable,
                                                         angle=90,
                                                         label=self._x_indicator_label+'={value:0.2f}',
                                                         pen=self._to_valid_rgb_(self._x_indicator_color),
                                                         labelOpts={'position': 0.1,
                                                                     'color': self._to_valid_rgb_(self._x_indicator_text_color),
                                                                     'fill': (0, 0, 0, 0),
                                                                     'movable': self._x_indicator_movable})
            self._x_position_indicator.sigPositionChanged.connect(self._x_position_indicator_changed_)
            self._plot.addItem(self._x_position_indicator)
            self._x_position_indicator.setValue(self._x_indicator_position)
        elif self._show_x_position_indicator:
            self._x_position_indicator.setPen(self._to_valid_rgb_(self._x_indicator_color))
            self._x_position_indicator.setMovable(self._x_indicator_movable)
            self._x_position_indicator.label.setFormat(self._x_indicator_label+'={value:0.2f}')
            self._x_position_indicator.label.setColor(self._to_valid_rgb_(self._x_indicator_text_color))
            self._x_position_indicator.label.setMovable(self._x_indicator_movable)
            self._x_position_indicator.setValue(self._x_indicator_position)

    def _x_position_indicator_changed_(self):
        value = self._x_position_indicator.value()
        self.x_position_indicator_changed.emit(value)

    def _set_x_axis_(self, value):
        """
        Sets a new x axis label while keeping the style
        :param value: text
        """
        self._x_label = value
        if self._plot is not None:
            self._plot.setLabel('bottom', value, color=self._to_html_color_(self._x_axis_color))
            self._plot.plotItem.axes['bottom']['item'].setPen(self._to_valid_rgb_(self._x_axis_color))

    def _set_y_axis_(self, value):
        """
        Sets a new y axis label while keeping the style
        :param value: text
        """
        self._y_label = value
        if self._plot is not None:
            self._plot.setLabel('left', value, color=self._to_html_color_(self._y_axis_color))
            self._plot.plotItem.axes['left']['item'].setPen(self._to_valid_rgb_(self._y_axis_color))

    def _fft_created_(self, freq, fft):
        """
        Callback when FFT creation has been finished
        :param freq: frequency data
        :param fft: amplitude data
        """
        if self._show_fft and self._fft_window is not None:
            self._close_fft_window_()
        elif not self._show_fft:
            self._show_fft = True
            self._fft_window = PyGraphSubPlotWindow(self)
            self._fft_window.setWindowTitle('FFT')
            fft_plot = PyGraphWidget(self._fft_window)
            fft_plot.set_data(freq, fft)
            fft_plot.set_plot_color('y')
            fft_plot.y_label = 'FFT amplitude'
            fft_plot.x_label = 'FFT frequency'
            self._fft_window.setCentralWidget(fft_plot)
            self._fft_window.is_closing.append(self._window_was_closed_)
            self._fft_window.show()

    def _window_was_closed_(self):
        """
        Callback when window is closed
        """
        if self._line_data is not None:
            self._line_data.setFftMode(False)
            self._show_fft = False

    def _close_fft_window_(self):
        """
        Callback when fft window is closed
        """
        if self._fft_window is not None:
            self._fft_window.close()
            self._show_fft = False

    def _range_changed_(self, *args):
        """
        Callback when range changes to update sampling for performance gain
        :param args: event arguments
        """
        self._plot.setDownsampling(ds=1, auto=False)
        self._plot.setClipToView(clip=False)
        self._plot.setDownsampling(auto=True)
        self._plot.setClipToView(clip=True)


class PyGraphSubPlotWindow(QMainWindow):
    """
    This window is used to display the FFT in a separate window
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_closing = list()

    def closeEvent(self, *args, **kwargs):
        for callback in self.is_closing:
            callback()
        return super().closeEvent(*args, **kwargs)


class PyGraphCustomPlotDataItem(pg.PlotDataItem):
    """
    This plot item overwrites the pyqtgraph PlotDataItem to fix a bug in the FFT option
    """

    def __init__(self, *args, **kwargs):
        self.fft_created = list()
        self.close_fft_window = list()
        super().__init__(*args, **kwargs)

    def setFftMode(self, mode):
        self.opts['fftMode'] = mode
        if mode:
            x = self.xData
            y = self.yData
            self.opts['fftMode'] = False
            freq, fft = self._fourierTransform(x, y)
            for callback in self.fft_created:
                callback(freq, fft)
        else:
            for callback in self.close_fft_window:
                callback()

    def _fourierTransform(self, x, y):
        fft = np.nan_to_num(np.real(np.fft.rfft(y)))
        freq = np.nan_to_num(np.fft.rfftfreq(len(y), d=(x[1] - x[0])))  # assume uniform spacing
        return freq, fft


if __name__ == '__main__':
        from pyqtgraph.Qt import QtGui
        from PyQt5.QtWidgets import QMainWindow
        from Model.Math.Spectrogram import spectrogram
        import h5py

        path = 'Z:/shared/Master Thesis/Experiments/TrappingExperiment/Trapping_30.4.2019/'
        file = 'trapping3_500mW.h5'
        hf = h5py.File(path+file, 'r')
        data = hf['data'][:]

        app = QtGui.QApplication([])
        main = QMainWindow()

        x_ = data[:, 0]
        y_ = data[:, 1]

        window_size = 4096
        overlap = round(window_size * 0.95)
        sampling_frequency = 1 / (x_[1] - x_[0])
        lower_limit_offset_dB = 10
        max_frequency = 25e3
        min_frequency = 0
        calc_spectra, calc_f, calc_t = spectrogram(y_, window_size, overlap, sampling_frequency,
                                                   f_min=min_frequency, f_max=max_frequency,
                                                   outlier_threshold_low=lower_limit_offset_dB)

        calc_f *= 1e-3
        plot = PyGraphWidget(main)
        plot.set_matplotlib_default_style()
        plot.title = 'test'
        plot.x_label = 't [s]'
        plot.y_label = 'stuff'
        plot.set_data(x_, y_)
        plot.set_imshow(calc_spectra, extent=(np.min(calc_t), np.max(calc_t), np.min(calc_f), np.max(calc_f)))
        plot.show_x_position_indicator = True
        plot.x_indicator_color = Qt.black
        plot.x_indicator_text_color = Qt.red
        plot.x_indicator_label = 'test'
        plot.x_indicator_position = 2
        print(plot.title)
        main.setCentralWidget(plot)
        main.show()
        QtGui.QApplication.instance().exec_()


def color_map_to_pyqtgraph(map):
    """
    Converts a colormap from matplotlib to a colormap for pyqtgraph.
    :param map: matplotlib colormap
    :return: pyqtgraph colormap
    """
    length = len(map.colors)
    pos = [i/length for i in range(length)]
    color = map.colors
    color_count = len(color[0])
    color_mode = None
    if color_count == 3:
        color_mode = ColorMap.RGB
        for entry in color:
            entry.append(1.)
    return ColorMap(pos, color, color_mode)


def pyqtgraph_color_map_from_matplotlib(name, lut=None):
    """
    Creates a colormap for pyqtgraph using matplotlib's colormap capabilities.
    :param name: map name
    :param lut: lookup table
    :return: pyqtgraph colormap
    """
    return color_map_to_pyqtgraph(get_cmap(name, lut))
