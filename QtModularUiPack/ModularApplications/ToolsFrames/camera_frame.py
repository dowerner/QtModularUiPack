from QtModularUiPack.Widgets import EmptyFrame
from QtModularUiPack.ModularApplications.ToolFrameViewModels.camera_frame_view_model import CameraFrameViewModel
from QtModularUiPack.Widgets.DataBinding import BindingEnabledWidget
from QtModularUiPack.Widgets.VideoExtensions import ImageRenderWidget
from PyQt5.QtWidgets import QVBoxLayout, QGridLayout, QDialog, QPushButton, QLabel, QSlider, QMenuBar, QComboBox, QSpinBox
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import cv2


class CameraFrame(EmptyFrame):
    name = 'Camera Viewer'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = CameraFrameViewModel()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame_)
        self.timer.start(1)

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._setup_()

    def _setup_(self):
        menu_bar = QMenuBar()
        menu_bar.setFixedHeight(22)
        connect_action = menu_bar.addAction('connect camera')
        settings_action = menu_bar.addAction('settings')
        options_menu = menu_bar.addMenu('options')
        auto_connect_action = options_menu.addAction('auto connect')
        auto_connect_action.setCheckable(True)
        auto_connect_action.setChecked(True)

        settings_action.triggered.connect(self._open_settings_)
        self._settings_dialog = None
        connect_action.triggered.connect(self._open_camera_selection_)
        self._camera_selection_dialog = None

        self._layout.addWidget(menu_bar)

        self._image_ = ImageRenderWidget()
        self._layout.addWidget(self._image_)

    def _open_settings_(self):
        if self._settings_dialog is not None:
            self._settings_dialog.close()
            self._settings_dialog = None

        self._settings_dialog = SettingsDialog(self.data_context, self)
        self._settings_dialog.setWindowModality(Qt.ApplicationModal)
        self._settings_dialog.show()

    def _open_camera_selection_(self):
        if self._camera_selection_dialog is not None:
            self._camera_selection_dialog.close()
            self._camera_selection_dialog = None
        self.data_context.disconnect_cam()
        self._camera_selection_dialog = CameraOpenDialog(self.data_context)
        self._camera_selection_dialog.setWindowModality(Qt.ApplicationModal)
        self._camera_selection_dialog.show()

    def _update_frame_(self):
        if not self.data_context.frame_queue.empty():
            frame = self.data_context.frame_queue.get()
            img = frame["frame"]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QImage(img.data, width, height, bpl, QImage.Format_RGB888)
            self._image_.set_image(image)


class CameraOpenDialog(QDialog, BindingEnabledWidget):

    def __init__(self, data_context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Open Camera')
        self.data_context = data_context
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self._setup_()

    def _connect_(self):
        self.data_context.connect_to_cam()
        self.close()

    def _setup_(self):
        camera_selection = QSpinBox()
        self._layout.addWidget(QLabel('camera:'), 0, 0)
        self._layout.addWidget(camera_selection, 0, 1)

        connect_button = QPushButton('connect')
        connect_button.clicked.connect(self._connect_)
        self._layout.addWidget(connect_button, 1, 1)

        self.bindings.set_binding('selected_camera', camera_selection, 'setValue')


class SettingsDialog(QDialog, BindingEnabledWidget):

    def __init__(self, data_context=None, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setWindowTitle('Camera Settings')
        self.data_context = data_context
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self._setup_()

    def _setup_(self):
        self._layout.addWidget(QLabel('Exposure Time:'), 0, 0)
        exposure_time = QLabel()
        exposure_time.setFixedWidth(40)
        self._layout.addWidget(exposure_time, 0, 2)
        self._layout.addWidget(QLabel('ms'), 0, 3)

        exposure_slider = QSlider(Qt.Horizontal)
        exposure_slider.setMinimum(0)
        exposure_slider.setMaximum(12)
        exposure_slider.setTickPosition(QSlider.TicksBelow)
        exposure_slider.setTickInterval(1)
        self.bindings.set_binding('exposure_time', exposure_time, 'setText')
        self.bindings.set_binding('exposure_time_index', exposure_slider, 'setValue')
        self._layout.addWidget(exposure_slider, 0, 1)


if __name__ == '__main__':
    CameraFrame.standalone_application()

