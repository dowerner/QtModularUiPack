from PyQt5.QtGui import QImage
from pyqtgraph import ColorMap
from matplotlib.colors import Colormap, ListedColormap
from matplotlib.pyplot import colormaps, get_cmap
from os.path import splitext, split
import numpy as np
import cv2


def get_color_map_from_file(path, delimiter=';', name=None):
    """
    Loads a colormap from a given file. The file should be delimiter separated and in the following format:
        0.1;0.11;0.12 ... 0.98;0.99;1.00    # red values
        0.2;0.21;0.25 ... 0.98;0.99;1.00    # green values
        0.21;0.21;0.22 ... 0.02;0.01;0.00   # blue values
    :param path: path of the colormap
    :param delimiter: delimiter in the file
    :param name: The name of the colormap. If not specified the filename will be used.
    :return: Listed colormap
    """
    if name is None:
        name = split(splitext(path)[0])[1]
    data = np.loadtxt(path, delimiter=delimiter)
    color_data = list()
    for i in range(data.shape[1]):
        color_data.append([data[0, i], data[1, i], data[2, i]])
    return ListedColormap(color_data, name=name)


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


class ColorMapImage(QImage):
    """
    This image is used as a representation of a colormap from matplotlib.
    """

    def __init__(self, color_map, *args, width=100, height=100, **kwargs):
        if type(color_map) == str:
            if color_map not in colormaps():
                raise Exception('The given name is not a valid color map.')
            self.color_map = get_cmap(color_map)
        elif isinstance(color_map, Colormap):
            self.color_map = color_map
        else:
            raise Exception('The given type cannot be used as a color map.')

        map_width = len(self.color_map.colors)
        c_map = self.color_map.colors
        color_count = len(c_map[0])
        data = np.array(c_map).reshape(1, map_width, color_count)
        self.red = data[0, :, 0]
        self.green = data[0, :, 1]
        self.blue = data[0, :, 2]

        data = cv2.resize(data, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
        data = np.int8(data * 255)

        height, width, bpc = data.shape
        bpl = bpc * width
        super().__init__(data.data.tobytes(), width, height, bpl, QImage.Format_RGB888)