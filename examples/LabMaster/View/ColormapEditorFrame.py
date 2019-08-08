from ViewModel.ColormapEditorViewModel import ColormapEditorViewModel
from Framework.Plotting.color_utils import ColorMapImage
from Widgets import EmptyFrame, PlotMasterWidget
from Widgets.QtExtensions import QRangeSlider
from Widgets.VideoExtensions import ImageRenderWidget
from PyQt5.QtWidgets import QGridLayout, QPushButton, QGroupBox, QMenuBar, QMainWindow, QScrollArea, QVBoxLayout, QLabel, QSpinBox
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from matplotlib.pyplot import colormaps, get_cmap
from matplotlib.colors import LinearSegmentedColormap
import numpy as np


class ColormapEditorFrame(EmptyFrame):

    name = 'Color Map Editor'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = ColormapEditorViewModel()
        self.data_context.set_ui_host(self)
        self.data_context.property_changed.connect(self._property_changed_)
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self._setup_()

    def _property_changed_(self, name):
        if name == 'red_values':
            self._red_plot.set_data(self.data_context.red_values)
        elif name == 'green_values':
            self._green_plot.set_data(self.data_context.green_values)
        elif name == 'blue_values':
            self._blue_plot.set_data(self.data_context.blue_values)
        if name == 'colors_minimum' or name == 'colors_maximum':
            x, y = self.data_context.red_values
            _, y_g = self.data_context.green_values
            _, y_b = self.data_context.blue_values

            if y_g is not None:
                y = np.concatenate([y, y_g])
            if y_b is not None:
                y = np.concatenate([y, y_b])

            self._plot.set_range(np.min(x), np.max(x), np.min(y), np.max(y))

    def _map_was_picked_(self, name):
        self.data_context.title = name
        self.data_context.import_from_matplot(name)

    def _import_matplotlib_colormap_(self):
        import_dialog = ColorMapPicker(self)
        import_dialog.color_was_picked.connect(self._map_was_picked_)
        import_dialog.show()

    def _add_range_slider_(self, color_name, grid_layout, row):
        grid_layout.addWidget(QLabel('{} range:'.format(color_name)), row, 0)
        slider_color = self.add_widget(QRangeSlider(), width=120, height=20)
        self.bindings.set_binding('colors_minimum', slider_color, 'setMin')
        self.bindings.set_binding('colors_maximum', slider_color, 'setMax')
        self.bindings.set_binding('{}_lower_boundary'.format(color_name), slider_color, 'setStart')
        self.bindings.set_binding('{}_upper_boundary'.format(color_name), slider_color, 'setEnd')
        grid_layout.addWidget(slider_color, row, 1)
        colors_lower_box = self.add_widget(QSpinBox(), '{}_lower_boundary'.format(color_name), 'setValue')
        self.bindings.set_binding('colors_minimum', colors_lower_box, 'setMinimum')
        self.bindings.set_binding('{}_upper_boundary'.format(color_name), colors_lower_box, 'setMaximum')
        grid_layout.addWidget(colors_lower_box, row, 2)
        colors_upper_box = QSpinBox()
        self.bindings.set_binding('{}_lower_boundary'.format(color_name), colors_upper_box, 'setMinimum')
        self.bindings.set_binding('colors_maximum', colors_upper_box, 'setMaximum')
        self.bindings.set_binding('{}_upper_boundary'.format(color_name), colors_upper_box, 'setValue')
        grid_layout.addWidget(colors_upper_box, row, 3)

    def _setup_(self):
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu('File')
        open_action = file_menu.addAction('Open')
        open_action.triggered.connect(self.data_context.open)
        save_action = file_menu.addAction('Save')
        save_action.triggered.connect(self.data_context.save)
        save_as_action = file_menu.addAction('Save As')
        save_as_action.triggered.connect(self.data_context.save_as)
        load_from_matplot_action = menu_bar.addAction('Import from Matplotlib')
        load_from_matplot_action.triggered.connect(self._import_matplotlib_colormap_)
        self._layout.addWidget(menu_bar, 0, 0, 1, 2, Qt.AlignLeft)

        self._plot = PlotMasterWidget()
        self.bindings.set_binding('title', self._plot, 'set_title')
        self._red_plot = self._plot.plot(0, 0, 'r', name='red', allow_remove=False)
        self._green_plot = self._plot.plot(0, 0, 'g', name='green', allow_remove=False)
        self._blue_plot = self._plot.plot(0, 0, 'b', name='blue', allow_remove=False)
        self._plot.set_xlabel('value')
        self._plot.set_ylabel('color value')
        self._layout.addWidget(self._plot, 1, 1)

        tool_box = QGroupBox('Tools')
        tool_box_layout = QGridLayout()
        tool_box_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tool_box.setLayout(tool_box_layout)
        self._layout.addWidget(tool_box, 1, 0)
        self._add_range_slider_('colors', tool_box_layout, 0)
        self._add_range_slider_('red', tool_box_layout, 1)
        self._add_range_slider_('green', tool_box_layout, 2)
        self._add_range_slider_('blue', tool_box_layout, 3)

        image_display = self.add_widget(ImageRenderWidget(keep_aspect_ratio=False), 'color_image', 'set_image', height=50)
        self._layout.addWidget(image_display, 2, 0, 1, 2, Qt.AlignJustify)


class ColorMapPicker(QMainWindow):
    color_was_picked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Import built-in matplotlib color-map')
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.WindowTitleHint)
        self.setFixedWidth(300)
        self._setup_()

    def _pick_colormap_(self, arg0, picked_name=None):
        self.color_was_picked.emit(picked_name)
        self.close()

    def _setup_(self):
        scroll_area = QScrollArea()
        self.setCentralWidget(scroll_area)
        scroll_layout = QVBoxLayout()
        scroll_layout.setAlignment(Qt.AlignCenter)
        scroll_area.setLayout(scroll_layout)
        group_box = QGroupBox()
        group_box.setLayout(scroll_layout)
        scroll_area.setWidget(group_box)
        scroll_area.setWidgetResizable(True)
        for map_name in colormaps():
            color_map = get_cmap(map_name)
            if type(color_map) != LinearSegmentedColormap:
                button = QPushButton(map_name)
                button.clicked.connect(lambda arg0, name=map_name: self._pick_colormap_(arg0, name))
                button.setFlat(True)
                button.setFixedSize(QSize(255, 20))
                button.setAutoFillBackground(True)
                im = ColorMapImage(color_map, width=255, height=20)
                palette = QPalette()
                palette.setBrush(button.backgroundRole(), QBrush(QPixmap.fromImage(im)))
                button.setPalette(palette)
                scroll_layout.addWidget(button)


if __name__ == '__main__':
    ColormapEditorFrame.standalone_application()
