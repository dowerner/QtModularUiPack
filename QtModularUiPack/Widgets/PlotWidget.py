from PyQt5.QtWidgets import QFrame, QSplitter, QVBoxLayout, QGridLayout, QScrollArea, QGroupBox, QLabel, QPushButton, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
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
        self._plot_config.set_title(title)

    def set_xlabel(self, value):
        self._plot_config.set_xlabel(value)

    def set_ylabel(self, value):
        self._plot_config.set_ylabel(value)

    def set_visibility(self, plot_item, visible):
        self._plot_config.set_visibility(plot_item, visible)

    def plot(self, *args, name=None, allow_remove=True, **kwargs):
        return self._plot_config.plot(*args, name=name, allow_remove=allow_remove, **kwargs)

    def set_xrange(self, lower, upper):
        self._plot_config.set_xrange(lower, upper)

    def set_yrange(self, lower, upper):
        self._plot_config.set_yrange(lower, upper)

    def set_range(self, xl, xu, yl, yu):
        self._plot_config.set_range(xl, xu, yl, yu)

    def remove(self, plot_item):
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

    def __init__(self, plot_widget: PlotWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plot_widget = plot_widget
        self._ax = self._plot_widget.add_subplot(111)
        self.plot_items = list()

        self._layout = QGridLayout()
        self.scroll_layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._setup_()

    def set_title(self, title):
        self._ax.set_title(title)
        self._plot_widget.update()

    def set_xlabel(self, value):
        self._ax.set_xlabel(value)
        self._plot_widget.update()

    def set_ylabel(self, value):
        self._ax.set_ylabel(value)
        self._plot_widget.update()

    def set_xrange(self, lower, upper):
        self._ax.set_xlim(lower, upper)
        self._plot_widget.update()

    def set_yrange(self, lower, upper):
        self._ax.set_ylim(lower, upper)
        self._plot_widget.update()

    def set_range(self, xl, xu, yl, yu):
        self.set_xrange(xl, xu)
        self.set_yrange(yl, yu)

    def set_visibility(self, plot_item, visible):
        plot_item.line_object._visible = visible
        self._plot_widget.update()

    def remove(self, plot_item):
        plot_item.line_object.remove()
        self.plot_items.remove(plot_item)
        self._fill_plot_list_()
        self._plot_widget.update()

    def update_legend(self):
        self._ax.legend([item.name for item in self.plot_items])

    def plot(self, *args, name=None, allow_remove=True, **kwargs):
        if name is None:
            name = 'plot item {}'.format(len(self.plot_items))

        line, = self._ax.plot(*args, **kwargs)
        plot_item = PlotWidgetItem(line, name, self._plot_widget, allow_remove, args, kwargs)
        self.plot_items.append(plot_item)

        self._fill_plot_list_()
        return plot_item

    def _fill_plot_list_(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

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

    @property
    def name(self):
        return self._plot_widget_item.name

    @name.setter
    def name(self, value):
        self._plot_widget_item.name = value

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
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

