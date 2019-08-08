from ViewModels import BaseViewModel
from Framework.Plotting.color_utils import ColorMapImage
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from matplotlib.colors import ListedColormap
from os.path import split, splitext
from scipy.interpolate import interp1d
import numpy as np


class ColormapEditorViewModel(BaseViewModel):

    name = 'color_map_editor'

    @property
    def red_values(self):
        return self._steps, self._red_values

    @red_values.setter
    def red_values(self, values):
        self._red_values = values
        self._steps = [i for i in range(len(values))]
        self.notify_change('red_values')

    @property
    def green_values(self):
        return self._steps, self._green_values

    @green_values.setter
    def green_values(self, values):
        self._green_values = values
        self._steps = [i for i in range(len(values))]
        self.notify_change('green_values')

    @property
    def blue_values(self):
        return self._steps, self._blue_values

    @blue_values.setter
    def blue_values(self, values):
        self._blue_values = values
        self._steps = [i for i in range(len(values))]
        self.notify_change('blue_values')

    @property
    def colors_minimum(self):
        return self._colors_minimum

    @colors_minimum.setter
    def colors_minimum(self, value):
        self._colors_minimum = value
        self.notify_change('colors_minimum')

    @property
    def colors_maximum(self):
        return self._colors_maximum

    @colors_maximum.setter
    def colors_maximum(self, value):
        self._colors_maximum = value
        self.notify_change('colors_maximum')

    @property
    def colors_lower_boundary(self):
        return self._colors_lower_boundary

    @colors_lower_boundary.setter
    def colors_lower_boundary(self, value):
        self._colors_lower_boundary = value
        self.rescale_colors(self._colors_lower_boundary, self._colors_upper_boundary)
        self._red_lower_boundary = value
        self._green_lower_boundary = value
        self._blue_lower_boundary = value
        self.notify_change('colors_lower_boundary')
        self.notify_change('red_lower_boundary')
        self.notify_change('blue_lower_boundary')
        self.notify_change('green_lower_boundary')
        self._update_image_()

    @property
    def colors_upper_boundary(self):
        return self._colors_upper_boundary

    @colors_upper_boundary.setter
    def colors_upper_boundary(self, value):
        self._colors_upper_boundary = value
        self.rescale_colors(self._colors_lower_boundary, self._colors_upper_boundary)
        self._red_upper_boundary = value
        self._green_upper_boundary = value
        self._blue_upper_boundary = value
        self.notify_change('colors_upper_boundary')
        self.notify_change('red_upper_boundary')
        self.notify_change('blue_upper_boundary')
        self.notify_change('green_upper_boundary')
        self._update_image_()

    @property
    def red_lower_boundary(self):
        return self._red_lower_boundary

    @red_lower_boundary.setter
    def red_lower_boundary(self, value):
        self._red_lower_boundary = value
        self.rescale_red(self._red_lower_boundary, self._red_upper_boundary)
        self.notify_change('red_lower_boundary')
        self._update_image_()

    @property
    def red_upper_boundary(self):
        return self._red_upper_boundary

    @red_upper_boundary.setter
    def red_upper_boundary(self, value):
        self._red_upper_boundary = value
        self.rescale_red(self._red_lower_boundary, self._red_upper_boundary)
        self.notify_change('red_upper_boundary')
        self._update_image_()

    @property
    def green_lower_boundary(self):
        return self._green_lower_boundary

    @green_lower_boundary.setter
    def green_lower_boundary(self, value):
        self._green_lower_boundary = value
        self.rescale_green(self._green_lower_boundary, self._green_upper_boundary)
        self.notify_change('green_lower_boundary')
        self._update_image_()

    @property
    def green_upper_boundary(self):
        return self._green_upper_boundary

    @green_upper_boundary.setter
    def green_upper_boundary(self, value):
        self._green_upper_boundary = value
        self.rescale_green(self._green_lower_boundary, self._green_upper_boundary)
        self.notify_change('green_upper_boundary')
        self._update_image_()

    @property
    def blue_lower_boundary(self):
        return self._blue_lower_boundary

    @blue_lower_boundary.setter
    def blue_lower_boundary(self, value):
        self._blue_lower_boundary = value
        self.rescale_blue(self._blue_lower_boundary, self._blue_upper_boundary)
        self.notify_change('blue_lower_boundary')
        self._update_image_()

    @property
    def blue_upper_boundary(self):
        return self._blue_upper_boundary

    @blue_upper_boundary.setter
    def blue_upper_boundary(self, value):
        self._blue_upper_boundary = value
        self.rescale_blue(self._blue_lower_boundary, self._blue_upper_boundary)
        self.notify_change('blue_upper_boundary')
        self._update_image_()

    @property
    def color_image(self):
        return self._color_image

    @color_image.setter
    def color_image(self, value):
        self._color_image = value
        self.notify_change('color_image')

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.notify_change('title')

    def __init__(self):
        super().__init__()
        self._loaded_file = None
        self._red_values = None
        self._raw_red = None
        self._green_values = None
        self._raw_green = None
        self._blue_values = None
        self._raw_blue = None
        self._steps = None
        self._colors_minimum = 0
        self._colors_maximum = 255
        self._colors_lower_boundary = 0
        self._colors_upper_boundary = 255
        self._red_lower_boundary = 0
        self._red_upper_boundary = 255
        self._green_lower_boundary = 0
        self._green_upper_boundary = 255
        self._blue_lower_boundary = 0
        self._blue_upper_boundary = 255
        self._color_image = None
        self._ui_host = None
        self._title = 'color curve'

    def set_ui_host(self, host):
        self._ui_host = host

    def _update_image_(self):
        data = np.vstack([self._red_values, self._green_values, self._blue_values])
        color_data = list()
        for i in range(data.shape[1]):
            color_data.append([data[0, i], data[1, i], data[2, i]])
        self.color_image = ColorMapImage(ListedColormap(color_data))

    def _rescale_color_(self, raw_color_data, lower, upper):
        cropped_data = raw_color_data[lower:upper]
        x = np.linspace(0, self.colors_maximum, len(cropped_data))
        f = interp1d(x, cropped_data)
        return f(self._steps)

    def rescale_red(self, lower, upper):
        self.red_values = self._rescale_color_(self._raw_red, lower, upper)

    def rescale_green(self, lower, upper):
        self.green_values = self._rescale_color_(self._raw_green, lower, upper)

    def rescale_blue(self, lower, upper):
        self.blue_values = self._rescale_color_(self._raw_blue, lower, upper)

    def rescale_colors(self, lower, upper):
        self.rescale_red(lower, upper)
        self.rescale_green(lower, upper)
        self.rescale_blue(lower, upper)

    def open(self):
        path, _ = QFileDialog.getOpenFileName(None, 'Open File', None, 'Color Map (*.csv)')
        if path == '':
            return

        try:
            data = np.loadtxt(path, delimiter=';')
            color_data = list()
            for i in range(data.shape[1]):
                color_data.append([data[0, i], data[1, i], data[2, i]])
            self._set_color_map_(ColorMapImage(ListedColormap(color_data)))
            self.title = splitext(split(path)[1])[0]
            self._loaded_file = path
        except Exception as e:
            QMessageBox.critical(self._ui_host, 'File Open Error', 'Error occurred while trying to open file: {}'.format(e))

    def save(self):
        if self._loaded_file is None:
            self.save_as()

        data = np.vstack([self._red_values, self._green_values, self._blue_values])
        np.savetxt(self._loaded_file, data, delimiter=';')

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(None, 'Save File', None, 'Color Map (*.csv)')
        if path == '':
            return

        self._loaded_file = path
        self.save()

    def _set_color_map_(self, map_image):
        self.color_image = map_image
        self.red_values = self.color_image.red
        self.green_values = self.color_image.green
        self.blue_values = self.color_image.blue
        self._raw_red = np.array(self._red_values)
        self._raw_green = np.array(self._green_values)
        self._raw_blue = np.array(self._blue_values)
        self.colors_minimum = 0
        self.colors_maximum = len(self.red_values[0]) - 1
        self.colors_upper_boundary = len(self.red_values[0]) - 1
        self.colors_lower_boundary = 0
        self.red_upper_boundary = len(self.red_values[0]) - 1
        self.red_lower_boundary = 0
        self.green_upper_boundary = len(self.green_values[0]) - 1
        self.green_lower_boundary = 0
        self.blue_upper_boundary = len(self.blue_values[0]) - 1
        self.blue_lower_boundary = 0

    def import_from_matplot(self, map_name):
        self._set_color_map_(ColorMapImage(map_name))

