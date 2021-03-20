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

from PyQt5.QtWidgets import QFrame, QSplitter, QHBoxLayout, QVBoxLayout, QGridLayout, QScrollArea, QGroupBox, QLabel, QPushButton, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams


class PlotMasterWidget(QFrame):
    """
    This widget shows a plot widget together with a plot config widget.
    """

    def __init__(self, *args, orientation=Qt.Horizontal, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        splitter = QSplitter(orientation)
        main_layout.addWidget(splitter)
        main_plot = PlotWidget(self)
        main_layout.addWidget(main_plot)
        self._plot_config = PlotConfig(main_plot)
        main_layout.addWidget(self._plot_config)

    def set_title(self, title):
        """
        Set plot title
        :param title: plot title
        """
        self._plot_config.set_title(title)

    def set_xlabel(self, value):
        """
        Set x-axis label of the plot
        :param value: x-axis label
        """
        self._plot_config.set_xlabel(value)

    def set_ylabel(self, value):
        """
        Set y-axis label of the plot
        :param value: y-axis label
        """
        self._plot_config.set_ylabel(value)

    def set_visibility(self, plot_item, visible):
        """
        Set visibility of the plot item
        :param plot_item: plot item
        :param visible: True for visible
        """
        self._plot_config.set_visibility(plot_item, visible)

    def plot(self, *args, name=None, allow_remove=True, **kwargs):
        """
        Plot data
        :param args: x and y data (as well as more matplotlib compatible arguments)
        :param name: name of the plot
        :param allow_remove: True or false
        :param kwargs: keyword arguments
        """
        return self._plot_config.plot(*args, name=name, allow_remove=allow_remove, **kwargs)

    def set_xrange(self, lower, upper):
        """
        Set x-axis range
        :param lower: left boundary
        :param upper: right boundary
        """
        self._plot_config.set_xrange(lower, upper)

    def set_yrange(self, lower, upper):
        """
        Set y-axis range
        :param lower: lower boundary
        :param upper: upper boundary
        """
        self._plot_config.set_yrange(lower, upper)

    def set_range(self, xl, xu, yl, yu):
        """
        Set plot range
        :param xl: left boundary
        :param xu: right boundary
        :param yl: lower boundary
        :param yu: upper boundary
        """
        self._plot_config.set_range(xl, xu, yl, yu)

    def remove(self, plot_item):
        """
        Remove plot item
        :param plot_item: plot item to remove
        """
        self._plot_config.remove(plot_item)


class PlotWidget(QFrame):
    """
    This widget provides an easy way to embed matplotlib plots into PyQt5 user interfaces
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._figure = None
        self._setup_()

    def update(self):
        """
        This method updates the plot according to the current settings
        """
        if self._figure is not None:
            self._figure.canvas.draw()

    def add_subplot(self, *args, **kwargs):
        """
        Adds subplot and returns the handle
        :param args: plot arguments
        :param kwargs: argument lists
        :return: ax handle
        """
        if self._figure is not None:
            return self._figure.add_subplot(*args, **kwargs)

    def _setup_(self):
        rcParams.update({'figure.autolayout': True})    # make sure that everything is visible (no cutoff labels)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self._figure = Figure()
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar(self._canvas, self)
        self._toolbar.setFixedHeight(30)
        self.layout.addWidget(self._canvas)
        self.layout.addWidget(self._toolbar)


class PlotConfig(QFrame):
    """
    This widget provides a configuration panel for manipulating plot widgets
    """

    def __init__(self, plot_widget: PlotWidget, *args, **kwargs):
        """
        Initialize plot config
        :param plot_widget: plot widget to access
        """
        super().__init__(*args, **kwargs)
        self._plot_widget = plot_widget
        self._ax = self._plot_widget.add_subplot(111)
        self.plot_items = list()

        self._layout = QGridLayout()
        self.scroll_layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._setup_()

    def set_title(self, title):
        """
        Set plot title
        :param title: plot title
        """
        self._ax.set_title(title)
        self._plot_widget.update()

    def set_xlabel(self, value):
        """
        Set x-axis label of the plot
        :param value: x-axis label
        """
        self._ax.set_xlabel(value)
        self._plot_widget.update()

    def set_ylabel(self, value):
        """
        Set y-axis label of the plot
        :param value: y-axis label
        """
        self._ax.set_ylabel(value)
        self._plot_widget.update()

    def set_xrange(self, lower, upper):
        """
        Set x-axis range
        :param lower: left boundary
        :param upper: right boundary
        """
        self._ax.set_xlim(lower, upper)
        self._plot_widget.update()

    def set_yrange(self, lower, upper):
        """
        Set y-axis range
        :param lower: lower boundary
        :param upper: upper boundary
        """
        self._ax.set_ylim(lower, upper)
        self._plot_widget.update()

    def set_range(self, xl, xu, yl, yu):
        """
        Set plot range
        :param xl: left boundary
        :param xu: right boundary
        :param yl: lower boundary
        :param yu: upper boundary
        """
        self.set_xrange(xl, xu)
        self.set_yrange(yl, yu)

    def set_visibility(self, plot_item, visible):
        """
        Set visibility of the plot item
        :param plot_item: plot item
        :param visible: True for visible
        """
        plot_item.line_object._visible = visible
        self._plot_widget.update()

    def remove(self, plot_item):
        """
        Remove plot item
        :param plot_item: plot item to remove
        """
        plot_item.line_object.remove()
        self.plot_items.remove(plot_item)
        self._fill_plot_list_()
        self._plot_widget.update()

    def update_legend(self):
        """
        Update legend according to plot items
        """
        self._ax.legend([item.name for item in self.plot_items])

    def plot(self, *args, name=None, allow_remove=True, **kwargs):
        """
        Plot data
        :param args: x and y data (as well as more matplotlib compatible arguments)
        :param name: name of the plot
        :param allow_remove: True or false
        :param kwargs: keyword arguments
        """
        if name is None:
            name = 'plot item {}'.format(len(self.plot_items))

        line, = self._ax.plot(*args, **kwargs)
        plot_item = PlotWidgetItem(line, name, self._plot_widget, allow_remove, args, kwargs)
        self.plot_items.append(plot_item)

        self._fill_plot_list_()
        return plot_item

    def _fill_plot_list_(self):
        """
        Fill plot configuration list
        """
        # remove existing items
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

        # fill list
        for item in self.plot_items:
            item_widget = EnableDisableWidget(item, self)
            self.scroll_layout.addWidget(item_widget)
        self.update_legend()

    def _setup_(self):
        self._layout.addWidget(QLabel('Plot Settings:'), 0, 0)

        scroll_area = QScrollArea()
        group_box = QGroupBox()
        group_box.setLayout(self.scroll_layout)
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll_area.setWidget(group_box)
        scroll_area.setWidgetResizable(True)
        self._layout.addWidget(scroll_area, 1, 0)


class PlotWidgetItem(object):
    """
    Data container for plot data
    """

    def set_data(self, *args):
        self.line_object.set_data(*args)
        self._plot_control.update()

    def __init__(self, line_object, name, plot_control, allow_remove, args, kwargs):
        self.line_object = line_object
        self._plot_control = plot_control
        self.allow_remove = allow_remove
        self.name = name
        self.args = args
        self.kwargs = kwargs


class EnableDisableWidget(QFrame):
    """
    Widget for controlling plot
    """

    @property
    def name(self):
        """
        Gets name of the plot
        """
        return self._plot_widget_item.name

    @name.setter
    def name(self, value):
        """
        Sets name of the plot
        :param value: name
        """
        self._plot_widget_item.name = value

    @property
    def enabled(self):
        """
        Gets if this plot is visible
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """
        Sets whether this plot is visible
        :param value: True means visible
        """
        self._enabled = value
        self._plot_control.set_visibility(self._plot_widget_item, self._enabled)
        self._enabled_box.setChecked(self._enabled)

    def __init__(self, plot_widget_item: PlotWidgetItem, plot_control: PlotConfig):
        super().__init__()
        self._plot_widget_item = plot_widget_item
        self._plot_control = plot_control
        self._enabled = True

        entry_layout = QHBoxLayout()
        entry_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(entry_layout)

        self._name_label = QLabel(plot_widget_item.name)
        self._enabled_box = QCheckBox(checked=True)
        self._enabled_box.stateChanged.connect(self._enabled_changed_)

        entry_layout.addWidget(self._name_label)
        entry_layout.addWidget(self._enabled_box)

        if plot_widget_item.allow_remove:
            remove_button = QPushButton('x')
            remove_button.clicked.connect(self._remove_)
            remove_button.setFixedWidth(20)
            entry_layout.addWidget(remove_button)

    def _enabled_changed_(self, *args):
        self.enabled = self._enabled_box.isChecked()

    def _remove_(self, *args):
        self._plot_control.remove(self._plot_widget_item)


if __name__ == '__main__':
    from PyQt5.Qt import QApplication
    from PyQt5.QtWidgets import QHBoxLayout, QMainWindow
    import numpy as np

    x = np.linspace(0, 6 * np.pi, 1000)
    y = np.cos(x)

    app = QApplication([])
    main = QMainWindow()

    layout = QHBoxLayout()
    content = QFrame()
    content.setLayout(layout)
    main.setCentralWidget(content)

    plot = PlotWidget(main)
    plot_handler = PlotConfig(plot)
    layout.addWidget(plot)
    layout.addWidget(plot_handler)

    plot_handler.plot(x, y, 'r--', name='cosine')
    plot_handler.plot(x, np.sin(x))

    main.show()
    QApplication.instance().exec_()

