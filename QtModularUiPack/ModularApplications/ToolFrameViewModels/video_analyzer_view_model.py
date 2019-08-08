from QtModularUiPack.ViewModels import BaseViewModel
from QtModularUiPack.Widgets.VideoExtensions import ImageLayer, ImageCircle, ImageEllipse, ImageRectangle, ImageShape
from QtModularUiPack.Framework import CodeEnvironment
from QtModularUiPack.Framework.Math import spectrogram
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QPushButton
from PyQt5.QtCore import QRect, pyqtSlot, QMetaObject, QObject, Qt, Q_ARG
from PyQt5.QtGui import QColor
from threading import Thread
from os.path import splitext, split
import sys
import numpy as np
import json
import h5py
import traceback


DEFAULT_IMPORT_CODE = '\n'.join(['"""',
                                 '# Use this code editor to add statements that have to be run only once.',
                                 '# e.g. imports or function definitions',
                                 '# add shapes that can be moved: c = add_circle(x=20, y=30, radius=15, border_color="red", fill_color=None)',
                                 '"""',
                                 'import cv2',
                                 'import numpy as np',
                                 '\nclear_overlay() # remove existing shapes on video'])
DEFAULT_FRAME_CODE = '\n'.join(['"""',
                                '# Use this code editor to process frames.',
                                '# Move shapes:     move(c, x=54, y=21)',
                                '# Change shapes:   change(c, radius=12, border_thickness=3)',
                                '"""',
                                'image = frame_data_image   # a numpy array containing the pixels of the current frame',
                                't = frame_data_time    # the time code of the current frame',
                                'result_data = t, 1     # plot flat line'])

DATA_MODE_TRACE = 'TIME_TRACE'
DATA_MODE_SPECTROGRAM = 'SPECTROGRAM'
DATA_MODES = [DATA_MODE_TRACE, DATA_MODE_SPECTROGRAM]


class VideoAnalyzerViewModel(QObject, BaseViewModel):

    name = 'video_analyzer'

    @property
    def video_path(self):
        return self._video_path

    @video_path.setter
    def video_path(self, value):
        self._video_path = value
        self.notify_change('video_path')

    @property
    def plot_data(self):
        return self._data_time, self._data_voltage

    @plot_data.setter
    def plot_data(self, value):
        self._data_time = value[0]
        self._data_voltage = value[1]
        self.notify_change('plot_data')

    @property
    def video_time_boundary_lower(self):
        return self._video_time_boundary_lower

    @video_time_boundary_lower.setter
    def video_time_boundary_lower(self, value):
        self._video_time_boundary_lower = value
        self.notify_change('video_time_boundary_lower')

    @property
    def video_time_boundary_upper(self):
        return self._video_time_boundary_upper

    @video_time_boundary_upper.setter
    def video_time_boundary_upper(self, value):
        self._video_time_boundary_upper = value
        self.notify_change('video_time_boundary_upper')

    @property
    def plot_time_boundary_lower(self):
        return self._plot_time_boundary_lower

    @plot_time_boundary_lower.setter
    def plot_time_boundary_lower(self, value):
        self._plot_time_boundary_lower = value
        self._plot_temporal_offset = -value
        self._set_plot_()
        self.data_mode = DATA_MODE_TRACE
        self.notify_change('plot_time_boundary_lower')
        self.notify_change('plot_temporal_offset')

    @property
    def plot_time_boundary_upper(self):
        return self._plot_time_boundary_upper

    @plot_time_boundary_upper.setter
    def plot_time_boundary_upper(self, value):
        self._plot_time_boundary_upper = value
        self._set_plot_()
        self.data_mode = DATA_MODE_TRACE
        self.notify_change('plot_time_boundary_upper')

    @property
    def plot_start(self):
        return self._plot_start

    @plot_start.setter
    def plot_start(self, value):
        self._plot_start = value
        self.data_mode = DATA_MODE_TRACE
        self.notify_change('plot_start')

    @property
    def plot_duration(self):
        return self._plot_duration

    @plot_duration.setter
    def plot_duration(self, value):
        self._plot_duration = value
        self.notify_change('plot_duration')

    @property
    def video_duration(self):
        return self._video_duration

    @video_duration.setter
    def video_duration(self, value):
        self._video_duration = value
        self.video_time_boundary_upper = value
        self.notify_change('video_duration')

    @property
    def plot_temporal_offset(self):
        return self._plot_temporal_offset

    @plot_temporal_offset.setter
    def plot_temporal_offset(self, value):
        self._plot_temporal_offset = value
        self._set_plot_()
        self.notify_change('plot_temporal_offset')

    @property
    def video_temporal_offset(self):
        return self._video_temporal_offset

    @video_temporal_offset.setter
    def video_temporal_offset(self, value):
        self._video_temporal_offset = value
        self.notify_change('video_temporal_offset')

    @property
    def plot_delta_time(self):
        return self._plot_delta_time

    @plot_delta_time.setter
    def plot_delta_time(self, value):
        self._plot_delta_time = value
        self.notify_change('plot_delta_time')

    @property
    def video_delta_time(self):
        return self._video_delta_time

    @video_delta_time.setter
    def video_delta_time(self, value):
        self._video_delta_time = value
        self.notify_change('video_delta_time')

    @property
    def current_time(self):
        return self._current_time

    @current_time.setter
    def current_time(self, value):
        self._current_time = value
        self.notify_change('current_time')

    @property
    def loaded_save(self):
        return self._loaded_save

    @property
    def import_editor_code(self):
        return self._import_editor_code

    @import_editor_code.setter
    def import_editor_code(self, value):
        self._import_editor_code = value
        self.notify_change('import_editor_code')

    @property
    def frame_editor_code(self):
        return self._frame_editor_code

    @frame_editor_code.setter
    def frame_editor_code(self, value):
        self._frame_editor_code = value
        self.notify_change('frame_editor_code')

    @property
    def ui_enabled(self):
        return self._ui_enabled

    @ui_enabled.setter
    def ui_enabled(self, value):
        self._ui_enabled = value
        self.notify_change('ui_enabled')

    @property
    def current_progress(self):
        return self._current_progress

    @current_progress.setter
    def current_progress(self, value):
        self._current_progress = value
        if self._progress_dialog is not None:
            self._progress_dialog.setValue(value)
        self.notify_change('current_progress')

    @property
    def import_code_path(self):
        return self._import_code_path

    @import_code_path.setter
    def import_code_path(self, value):
        self._import_code_path = value
        if value is not None:
            with open(value, 'r') as file:
                self.import_editor_code = file.read()

    @property
    def frame_code_path(self):
        return self._frame_code_path

    @frame_code_path.setter
    def frame_code_path(self, value):
        self._frame_code_path = value
        if value is not None:
            with open(value, 'r') as file:
                self.frame_editor_code = file.read()

    @property
    def result_plot_data(self):
        return self._result_plot_time, self._result_plot_data

    def set_result_plot_data(self, t, y):
        self._result_plot_time = t
        self._result_plot_data = y
        self.notify_change('result_plot_data')

    @property
    def data_mode(self):
        return self._data_mode

    @data_mode.setter
    def data_mode(self, value):
        if value not in DATA_MODES:
            print('The given value "{}" is not a valid data mode.'.format(value))
            value = DATA_MODE_TRACE

        if value == DATA_MODE_SPECTROGRAM and self._data_spectrogram is None and self._data_time is not None:
            fs = 1 / (self._data_time[1] - self._data_time[0])
            self._data_spectrogram, f, t = spectrogram(self._data_voltage, 4096, int(0.95 * 4096), fs, 25e3)
            self._spectrogram_range = (np.min(t), np.max(t), np.min(f)*1e-3, np.max(f)*1e-3)

        if value == DATA_MODE_SPECTROGRAM:
            self.notify_change('spectrogram')

        self._data_mode = value
        self.notify_change('data_mode')

    @property
    def spectrogram(self):
        return self._data_spectrogram

    @property
    def spectrogram_range(self):
        return self._spectrogram_range

    @property
    def video_overlay(self):
        return self._video_overlay

    @property
    def video_editor(self):
        return self._video_editor

    @video_editor.setter
    def video_editor(self, editor):
        self._video_editor = editor
        editor.meta_data_loaded.connect(self._set_parameters_after_meta_data_)

    def __init__(self):
        super().__init__()
        self._loaded_save = None
        self._ui_enabled = True
        self._ui_host = None
        self._progress_dialog = None
        self._async_error_title = None
        self._async_error_message = None
        self._data_mode = DATA_MODE_TRACE
        self._current_progress = 0
        self._asynchronous_action = None
        self._cancel_async_action = False
        self._data_time = None
        self._raw_data_time = None
        self._data_spectrogram = None
        self._spectrogram_range = None
        self._data_voltage = None
        self._raw_data_voltage = None
        self.auto_fit_plot_data = True
        self._result_plot_data = None
        self._result_plot_time = None
        self._video_path = None
        self._trace_data = None
        self._plot_start = 0
        self._plot_duration = 0
        self._plot_temporal_offset = 0
        self._video_duration = 0
        self._video_temporal_offset = 0
        self._current_time = 0
        self._video_delta_time = 1
        self._plot_delta_time = 1
        self._video_time_boundary_lower = 0
        self._plot_time_boundary_lower = 0
        self._video_time_boundary_upper = 0
        self._plot_time_boundary_upper = 0
        self.code_environment = CodeEnvironment()
        self._setup_auxiliary_methods_()
        self._video_editor = None
        self._video_overlay = ImageLayer(True)
        self._import_editor_code = DEFAULT_IMPORT_CODE
        self._frame_editor_code = DEFAULT_FRAME_CODE
        self._import_code_path = None
        self._frame_code_path = None
        self._roi = None
        self._video_upper_boundary = 0
        self._video_lower_boundary = 0
        self._export_video_path = None

    def _set_plot_(self):
        if self._raw_data_time is None or len(self._raw_data_time) == 0:
            return
        idx = (self._raw_data_time >= self.plot_time_boundary_lower) & (self._raw_data_time <= self.plot_time_boundary_upper)
        x_data = self._raw_data_time[idx] + self.plot_temporal_offset
        y_data = self._raw_data_voltage[idx]

        if len(x_data) > 1:
            self.plot_data = (x_data, y_data)

    def set_ui_host(self, host):
        self._ui_host = host

    @pyqtSlot(str, str)
    def message_error(self, message, title):
        if self._ui_host is None:
            print('error message: {}'.format(message))
        else:
            QMessageBox.critical(self._ui_host, title, message)

    def _cancel_async_(self, *args):
        self._cancel_async_action = True

    def run_asynchronous(self, action, title='Action Executing', text='Progress...', error_message='Error while running action', error_title='Error'):
        self.ui_enabled = False
        self._asynchronous_action = action
        self._cancel_async_action = False
        self._progress_dialog = QProgressDialog(title, None, 0, 100)
        self._progress_dialog.setWindowTitle(title)
        self._progress_dialog.setLabelText(text)
        self._async_error_message = error_message
        self._async_error_title = error_title
        self._progress_dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self._cancel_async_)
        self._progress_dialog.setCancelButton(cancel_button)
        self._current_progress = 0
        self._progress_dialog.show()
        thread = Thread(target=self._asynchronous_worker_, daemon=True)
        thread.start()

    @pyqtSlot()
    def _close_progress_(self):
        if self._progress_dialog is not None:
            self._progress_dialog.close()
            self._progress_dialog = None
        self.ui_enabled = True

    @pyqtSlot(float)
    def _set_progress_(self, progress):
        self.current_progress = progress

    def _asynchronous_worker_(self):
        error = False
        caught_exception = None
        try:
            self._asynchronous_action()
        except Exception as e:
            error = True
            caught_exception = e
            traceback.print_exc()

        QMetaObject.invokeMethod(self, '_close_progress_')
        if error:
            QMetaObject.invokeMethod(self, 'message_error', Q_ARG(str, '{}: {}'.format(self._async_error_message, caught_exception)), Q_ARG(str, self._async_error_title))

    def set_time_silent(self, seconds):
        self._current_time = seconds

    @staticmethod
    def _to_qt_color_(color_description):
        if color_description is None:
            return Qt.transparent
        if type(color_description) == list or type(color_description) == tuple:
            return QColor(*color_description)
        elif type(color_description) == str:
            return getattr(Qt, color_description)

    def _setup_auxiliary_methods_(self):
        def add_ellipse(x, y, width, height, border_color='red', fill_color=None):
            filled = fill_color is not None
            b_color = self._to_qt_color_(border_color)
            f_color = self._to_qt_color_(fill_color)
            ellipse = ImageEllipse(x=x, y=y, width=width, height=height, border_color=b_color, filled=filled, fill_color=f_color)
            self.video_overlay.shapes.append(ellipse)
            return ellipse

        def add_circle(x, y, radius, border_color='red', fill_color=None):
            filled = fill_color is not None
            b_color = self._to_qt_color_(border_color)
            f_color = self._to_qt_color_(fill_color)
            circle = ImageCircle(x=x, y=y, radius=radius, border_color=b_color, filled=filled, fill_color=f_color)
            self.video_overlay.shapes.append(circle)
            return circle

        def add_rectangle(x, y, width, height, border_color='red', fill_color=None):
            filled = fill_color is not None
            b_color = self._to_qt_color_(border_color)
            f_color = self._to_qt_color_(fill_color)
            rectangle = ImageRectangle(x=x, y=y, width=width, height=height, border_color=b_color, filled=filled, fill_color=f_color)
            self.video_overlay.shapes.append(rectangle)
            return rectangle

        def clear_overlay():
            self.video_overlay.shapes.clear()

        def set_roi(x, y, width, height):
            self.video_editor.set_roi(QRect(x, y, width, height))

        def get_roi():
            return [self.video_editor.roi.x(), self.video_editor.roi.y(), self.video_editor.roi.width(), self.video_editor.roi.height()]

        self.code_environment.local_variables['add_circle'] = add_circle
        self.code_environment.local_variables['add_ellipse'] = add_ellipse
        self.code_environment.local_variables['add_rectangle'] = add_rectangle
        self.code_environment.local_variables['clear_overlay'] = clear_overlay
        self.code_environment.local_variables['set_roi'] = set_roi
        self.code_environment.local_variables['get_roi'] = get_roi

    def run_on_current_frame(self):
        current_frame = self.video_editor.current_frame
        local_plot_time, local_plot_data = self.plot_data

        if self._result_plot_time is None:
            self.set_result_plot_data(list(), list())

        if 'result_data' in self.code_environment.local_variables:
            del self.code_environment.local_variables['result_data']

        def move(shape: ImageShape, x, y):
            shape.add_keyframe(current_frame, position=(x, y))

        def change(shape: ImageShape, **kwargs):
            shape.add_keyframe(current_frame, **kwargs)

        self.code_environment.local_variables['move'] = move
        self.code_environment.local_variables['change'] = change
        self.code_environment.local_variables['frame_data_image'] = self.video_editor.get_frame(current_frame)
        self.code_environment.local_variables['frame_data_time'] = self.video_editor.get_time(current_frame)
        self.code_environment.local_variables['plot_time'] = local_plot_time
        self.code_environment.local_variables['plot_data'] = local_plot_data
        self.code_environment.local_variables['frame_count'] = self.video_editor.frame_count
        self.code_environment.local_variables['start_frame'] = self.video_editor.start_frame
        self.code_environment.local_variables['end_frame'] = self.video_editor.end_frame
        self.code_environment.local_variables['current_frame'] = current_frame
        if self._loaded_save is not None:
            self.code_environment.local_variables['project_folder'] = split(self._loaded_save)[0]
        self.code_environment.local_variables['apply_on_all_frames'] = False

        self.code_environment.run(self.import_editor_code)
        self.code_environment.run(self.frame_editor_code)

        if 'result_data' in self.code_environment.local_variables:
            t, y = self.code_environment.local_variables['result_data']
            self._result_plot_time.append(t)
            self._result_plot_data.append(y)
            self.notify_change('result_plot_data')

    def _run_on_entire_clip_(self):
        local_plot_time, local_plot_data = self.plot_data
        if self._loaded_save is not None:
            self.code_environment.local_variables['project_folder'] = split(self._loaded_save)[0]
        self.code_environment.local_variables['frame_count'] = self.video_editor.frame_count
        self.code_environment.local_variables['start_frame'] = self.video_editor.start_frame
        self.code_environment.local_variables['end_frame'] = self.video_editor.end_frame
        self.code_environment.local_variables['plot_time'] = local_plot_time
        self.code_environment.local_variables['plot_data'] = local_plot_data
        self.code_environment.local_variables['apply_on_all_frames'] = True
        self.code_environment.local_variables['current_frame'] = 0
        first_frame = int(self.video_editor.start_frame)
        last_frame = int(self.video_editor.end_frame)
        step = 100. / float(last_frame - first_frame)
        progress = 0
        QMetaObject.invokeMethod(self, '_set_progress_', Q_ARG(float, progress))
        self.current_progress = 0
        self.code_environment.run(self.import_editor_code, raise_exceptions=True)

        for current_frame in range(first_frame, last_frame + 1):
            if self._cancel_async_action:
                print('Operation canceled.')
                return

            def move(shape: ImageShape, x, y):
                shape.add_keyframe(current_frame, position=(x, y))

            def change(shape: ImageShape, **kwargs):
                shape.add_keyframe(current_frame, **kwargs)

            if 'result_data' in self.code_environment.local_variables:
                del self.code_environment.local_variables['result_data']

            self.code_environment.local_variables['move'] = move
            self.code_environment.local_variables['current_frame'] = current_frame
            self.code_environment.local_variables['change'] = change
            self.video_editor.current_frame = current_frame
            self.code_environment.local_variables['frame_data_image'] = self.video_editor.get_frame(current_frame, wait_for_new_frame=True)
            self.code_environment.local_variables['frame_data_time'] = self.video_editor.get_time(current_frame)
            self.code_environment.run(self.frame_editor_code, raise_exceptions=True)
            if self.current_progress < 100:
                progress += step
                QMetaObject.invokeMethod(self, '_set_progress_', Q_ARG(float, progress))

            if 'result_data' in self.code_environment.local_variables:
                t, y = self.code_environment.local_variables['result_data']
                self._result_plot_time.append(t)
                self._result_plot_data.append(y)
                self.notify_change('result_plot_data')
        print('done.')

    def run_on_entire_clip(self):
        self.set_result_plot_data(list(), list())
        self.run_asynchronous(self._run_on_entire_clip_, 'Processing Video',
                              'Image processing code is being applied to every frame.',
                              'An error occurred during the processing of the video file',
                              'Error while processing')

    def import_video(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(None, 'Import Video File', None, 'Video File (*.avi)')
            if path == '':
                return
        self._roi = None
        self.video_path = path

    def _import_data_(self, path):
        self.auto_fit_plot_data = True
        self._trace_data = path
        x, y = h5py.File(path, 'r')['data'][:].T
        self._raw_data_time = x
        self._raw_data_voltage = y
        self._data_spectrogram = None
        self.plot_start = x[0]
        self.plot_duration = x[-1]
        self.plot_time_boundary_lower = x[0]
        self.plot_time_boundary_upper = self._plot_duration
        self.auto_fit_plot_data = False
        if len(x) > 1:
            self.plot_delta_time = x[1] - x[0]
            self.plot_temporal_offset = -x[0]

    def import_data(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(None, 'Import Time Trace', None, 'Measured Data (*.h5)')
            if path == '':
                return

        try:
            self._import_data_(path)
        except Exception as e:
            self.message_error('Error while importing time trace: {}'.format(e), 'Import Error')

    def save(self):
        if self._loaded_save is None:
            self.save_as()

        path_base = splitext(self._loaded_save)[0]
        import_code_path = '{}_import_code.py'.format(path_base)
        frame_code_path = '{}_frame_code.py'.format(path_base)

        roi = self.video_editor.roi
        if self.video_editor.roi is None:
            roi = QRect(0, 0, self.video_editor.video_width, self.video_editor.video_height)

        data = {'trace_data': self._trace_data,
                'plot_time_boundary_lower': self.plot_time_boundary_lower,
                'plot_time_boundary_upper': self.plot_time_boundary_upper,
                'plot_temporal_offset': self.plot_temporal_offset,
                'video_path': self._video_path,
                'video_time_boundary_lower': self.video_time_boundary_lower,
                'video_time_boundary_upper': self.video_time_boundary_upper,
                'ROI_x': roi.x(),
                'ROI_y': roi.y(),
                'ROI_width': roi.width(),
                'ROI_height': roi.height(),
                'current_time': self.current_time,
                'import_code_path': import_code_path,
                'frame_code_path': frame_code_path}

        json_data = json.dumps(data, indent=1)  # generate json string

        try:
            with open(self._loaded_save, 'w') as file:
                file.write(json_data)  # write json string to file
            with open(import_code_path, 'w') as file:
                file.write(self.import_editor_code)
            with open(frame_code_path, 'w') as file:
                file.write(self.frame_editor_code)
        except Exception as e:
            self.message_error('Unable to save file: {}'.format(e), 'Error while saving')

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(None, 'Save File', None, 'Video Analysis File (*.json)')
        if path == '':
            return

        self._loaded_save = path
        self.save()

    def _set_property_(self, property, key, data):
        if key in data:
            setattr(self, property, data[key])

    def _set_parameters_after_meta_data_(self, meta_data):
        if self._roi is not None:
            self.video_editor.set_roi(self._roi)
            self.video_time_boundary_upper = self._video_upper_boundary
            self.video_time_boundary_lower = self._video_lower_boundary

    def open(self):
        path, _ = QFileDialog.getOpenFileName(None, 'Open File', None, 'Video Analysis File (*.json)')
        if path == '':
            return

        try:
            with open(path, 'r') as file:
                data = json.loads(file.read())  # retrieve dictionary representing the frame hierarchy from json file
                if data['trace_data'] is not None:
                    self._import_data_(data['trace_data'])
                if data['video_path'] is not None:
                    self.import_video(data['video_path'])
                self._set_property_('plot_time_boundary_lower', 'plot_time_boundary_lower', data)
                self._set_property_('plot_time_boundary_upper', 'plot_time_boundary_upper', data)
                self._set_property_('plot_temporal_offset', 'plot_temporal_offset', data)
                self._set_property_('current_time', 'current_time', data)
                self._set_property_('import_code_path', 'import_code_path', data)
                self._set_property_('frame_code_path', 'frame_code_path', data)
                self._video_upper_boundary = data['video_time_boundary_upper']
                self._video_lower_boundary = data['video_time_boundary_lower']
                self._roi = QRect(data['ROI_x'], data['ROI_y'], data['ROI_width'], data['ROI_height'])
                self._loaded_save = path
                sys.path.append(split(path)[0])
        except Exception as e:
            self.message_error('Error while opening analysis file. {}'.format(e), 'File Open Error')

    def _export_video_worker_(self):
        import cv2      # do import here in case OpenCV is not installed, the rest of the app still works

        width = self.video_editor.video_width
        height = self.video_editor.video_height
        if self.video_editor.roi is not None:
            width = self.video_editor.roi.width()
            height = self.video_editor.roi.height()

        video_file = cv2.VideoWriter(self._export_video_path,
                                     0x00000021,
                                     self.video_editor.fps,
                                     (width, height))
        first_frame = int(self.video_editor.start_frame)
        last_frame = int(self.video_editor.end_frame)
        step = 100. / float(last_frame - first_frame)
        progress = 0
        QMetaObject.invokeMethod(self, '_set_progress_', Q_ARG(float, progress))

        for current_frame in range(first_frame, last_frame + 1):
            if self._cancel_async_action:
                video_file.release()
                print('Operation canceled.')
                return

            self.video_editor.current_frame = current_frame
            frame_data = self.video_editor.get_frame(current_frame, wait_for_new_frame=True)
            #frame_data = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
            video_file.write(frame_data)

            if self.current_progress < 100:
                progress += step
                QMetaObject.invokeMethod(self, '_set_progress_', Q_ARG(float, progress))

        video_file.release()
        print('Video exported to: {}'.format(self._export_video_path))

    def export_video(self):
        self._export_video_path, _ = QFileDialog.getSaveFileName(None, 'Export Video', None, 'Video File (*.mp4)')
        if self._export_video_path == '':
            return
        self.run_asynchronous(self._export_video_worker_, 'Exporting Video',
                              'Video is being exported please wait...',
                              'An error occurred during export',
                              'Error while exporting')

    def export_result_plot(self):
        path, _ = QFileDialog.getSaveFileName(None, 'Export Data', None, 'Plot Data (*.h5)')
        if path == '':
            return

        try:
            data = np.array(self.result_plot_data).T
            file = h5py.File(path, 'w')
            file.create_dataset('data', data=data)
            file.close()
        except Exception as e:
            self.message_error('Error while exporting data. {}'.format(e), 'File Export Error')
