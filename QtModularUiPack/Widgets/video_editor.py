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

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QSizePolicy, QLabel, QStyle, QPushButton, QSpinBox
from PyQt5.QtCore import Qt, QPoint, QSize, QRect, QEvent, QUrl, pyqtSignal
from QtModularUiPack.Widgets.VideoExtensions import ImageRenderWidget, ImageLayer, ImageRectangle, VideoFrameGrabber
from QtModularUiPack.Widgets.QtExtensions import QJumpSlider
from time import sleep
import numpy as np


class VideoEditor(QFrame):
    """
    This widget allows to load a video file and zoom onto a specific ROI (region of interest)
    """

    meta_data_loaded = pyqtSignal(dict)

    @property
    def is_playing(self):
        """
        True if the video is currently being played.
        """
        return self._media_player.state() == QMediaPlayer.PlayingState

    @property
    def duration(self):
        """
        Duration in seconds of the video clip currently loaded.
        """
        return self._duration

    @property
    def start_trim(self):
        """
        Gets the duration of the trimmed footage at the beginning of the video clip in seconds.
        """
        return self._start_trim

    @start_trim.setter
    def start_trim(self, value):
        """
        Sets how much of the beginning of the clip should be trimmed.
        :param value: Footage to cut in seconds
        """
        if not self.video_file_open:
            return
        if value > self.end_trim:
            value = self.end_trim
        if value < 0:
            value = 0

        self._start_trim = value
        self._start_frame = int(value * self.fps)
        self._timeline.setMinimum(value * 1000)
        self._current_time.setText('{:10.3f}'.format(round(self._timeline.value() / self.fps / 1000 - self._start_trim, 3)))
        self._total_time.setText('{:10.3f}'.format(self._end_trim - self._start_trim))

    @property
    def end_trim(self):
        """
        Gets the time in seconds until which the video clip is shown. The rest is trimmed.
        """
        return self._end_trim

    @end_trim.setter
    def end_trim(self, value):
        """
        Sets the time in seconds until which the video clip is displayed. Everything beyond is trimmed.
        :param value: Time code in seconds until which the video clip shoud be shown
        """
        if not self.video_file_open:
            return
        if value > self._duration_time_code / 1000:
            value = self._duration_time_code / 1000
        if value < self._start_trim:
            value = self._start_trim

        self._end_trim = value
        self._end_frame = int(value * self.fps)
        self._timeline.setMaximum(value * 1000)
        self._current_time.setText('{:10.3f}'.format(round(self._timeline.value() / self.fps / 1000 - self._start_trim, 3)))
        self._total_time.setText('{:10.3f}'.format(self._end_trim - self._start_trim))

    @property
    def fps(self):
        """
        Frames per second of the currently loaded video clip.
        """
        return self._fps

    @property
    def frame_count(self):
        """
        Total amount of frames of the currently loaded video clip.
        """
        return self._frame_count

    @property
    def current_frame(self):
        """
        Gets the current frame
        """
        return self._current_frame

    @current_frame.setter
    def current_frame(self, value):
        """
        Sets the current frame
        :param value: frame number
        """
        self._current_frame = value
        self._allow_frame_counter_update = False
        self._media_player.setPosition(self._frame_number_to_time_code(value))
        self._allow_frame_counter_update = True

    @property
    def start_frame(self):
        """
        Gets the start frame. (Depends on the trimming of the video clip)
        """
        return self._start_frame

    @property
    def end_frame(self):
        """
        Gets the end frame. (Depends on the trimming of the video clip)
        """
        return self._end_frame

    @property
    def video_width(self):
        """
        Horizontal resolution of the currently loaded video clip.
        """
        return self._video_width

    @property
    def video_height(self):
        """
        Vertical resolution of the currently loaded video clip.
        """
        return self._video_height

    @property
    def video_path(self):
        """
        Path of the currently loaded video file.
        """
        return self._video_path

    @property
    def video_file_open(self):
        """
        True if a video file is currently opened in the editor.
        """
        return self._video_file_open

    @property
    def roi(self):
        """
        Returns a QRect representing the current region of interest. (If None, the entire image is the ROI)
        """
        return self._roi

    @property
    def overlay_layers(self):
        return self._image_control.overlay_layers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installEventFilter(self)   # start listening for mouse events to capture ROI changes
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)    # make the editor use as much space as possible
        self._media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self._media_player.positionChanged.connect(self._player_time_changed_)
        self._media_player.metaDataAvailableChanged.connect(self._meta_data_changed_)
        self._grabber = VideoFrameGrabber(self)
        self._allow_frame_counter_update = True
        self._result_frame = None
        self._media_player.setVideoOutput(self._grabber)
        self._grabber.frameAvailable.connect(self._frame_ready_)
        self._video_file_open = False
        self._video_path = None
        self._display_image = dict()    # cache for images that are displayed from the video
        self._frame_count = 0
        self._duration_time_code = 0
        self._duration = 0
        self._fps = 1
        self._current_frame = 0
        self._video_width = 0
        self._video_height = 0
        self._file_path = None
        self._is_playing = False
        self._roi = None
        self._start_trim = 0
        self._end_trim = 0
        self._start_frame = 0
        self._end_frame = 0
        self._layers = list()   # layers for visualizations on top of the video footage
        self._selection_layer = ImageLayer(enabled=False)   # layer for selection indicators
        self._selection_rectangle = ImageRectangle(0, 0, filled=False, border_color=Qt.yellow)  # selection rectangle
        self._selection_layer.shapes.append(self._selection_rectangle)
        self._selection_start = None    # start point for selection rectangle
        self.time_code_changed = list()

        self._layout = QGridLayout()
        self._timeline = None
        self._current_time = None
        self._total_time = None
        self._frame_box = None
        self._play_button = None
        self._stop_button = None
        self._next_frame_button = None
        self._previous_frame_button = None
        self._box_roi_x = None
        self._box_roi_y = None
        self._box_roi_width = None
        self._box_roi_height = None
        self._accept_roi_updates_from_boxes = True
        self._wait = False

        self.setLayout(self._layout)
        self._setup_()

    def _time_code_to_frame_number_(self, time_code):
        """
        Convert time code to frame number
        :param time_code: time code (in ms)
        :return: frame number
        """
        return int(time_code / 1000 * self.fps)

    def _frame_number_to_time_code(self, f_number):
        """
        Convert frame number to time code
        :param f_number: frame number
        :return: time code (in ms)
        """
        return int(f_number / self.fps * 1000)

    def _to_image_space_(self, point: QPoint):
        """
        Convert a point on the editor widget in to a point in the video footage.
        :param point: point in coordinates of the widget
        :return: point in the coordinates of the video footage
        """
        control_position = self._image_control.pos()    # get the position of the video image on the editor
        control_size = self._image_control.size()   # get the size of the video image
        dx = (control_size.width() - self._image_control.image_width) / 2   # get the x offset of the footage in the image
        dy = (control_size.height() - self._image_control.image_height) / 2     # get the y offset of the footage in the image
        x = (point.x() - dx - control_position.x()) / self._image_control.image_scale_x
        y = (point.y() - dy - control_position.y()) / self._image_control.image_scale_y
        return QPoint(x, y)

    def eventFilter(self, obj, event):
        """
        Check for mouse events to edit the ROI
        :param obj: object that caused the event
        :param event: event parameters (i.e. mouse position on the widget)
        """
        if event.type() == QEvent.MouseMove:    # if the mouse was moved, update the selection size
            target = self._to_image_space_(event.pos())
            self._selection_rectangle.position = self._selection_start
            self._selection_rectangle.width = target.x() - self._selection_start.x()
            self._selection_rectangle.height = target.y() - self._selection_start.y()
            self._image_control.update()
        elif event.type() == QEvent.MouseButtonPress:   # if the left mouse button was pressed designate the point as start of the selection
            self._selection_layer.enabled = True
            target = self._to_image_space_(event.pos())
            self._selection_start = target
        elif event.type() == QEvent.MouseButtonRelease and self._selection_start is not None:   # if the button was release the the ROI
            self._selection_layer.enabled = False
            end_point = self._to_image_space_(event.pos())

            # get all possible corner points
            x1 = self._selection_start.x()
            x2 = end_point.x()
            y1 = self._selection_start.y()
            y2 = end_point.y()

            # find upper left corner of the ROI
            roi_x = x1 if x1 < x2 else x2
            roi_y = y1 if y1 < y2 else y2

            # find extent of the ROI
            roi_width = abs(x1 - x2)
            roi_height = abs(y1 - y2)

            # set the ROI if it was not just a click with no extent
            if roi_width > 0 and roi_height > 0:
                # take into account if the footage was already focused onto a previous ROI
                if self._roi is not None:
                    roi_x += self._roi.x()
                    roi_y += self._roi.y()

                # update spin box values
                self._accept_roi_updates_from_boxes = False     # disable ROI changes from the spin boxes
                self._box_roi_x.setValue(roi_x)
                self._box_roi_y.setValue(roi_y)
                self._box_roi_width.setValue(roi_width)
                self._box_roi_height.setValue(roi_height)
                self._accept_roi_updates_from_boxes = True  # enable ROI changes from the spin boxes
                self.set_roi(QRect(roi_x, roi_y, roi_width, roi_height))   # set ROI
                self._selection_start = None    # remove selection start
        return False

    def sizeHint(self):
        """
        Needed for widget to expand properly on the UI (Should be improved)
        """
        return QSize(1200, 1200)

    def load(self, path):
        """
        Load a video file from the given path
        :param path: path of the file
        """
        if self.video_file_open:    # close current video file if one was open
            self.close()

        self._media_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self._video_file_open = True
        self._media_player.pause()

    def _player_time_changed_(self, position):
        self._timeline.setValueSilent(position)
        if self._allow_frame_counter_update:
            self._current_frame = self._time_code_to_frame_number_(position)

        # used for updating keyframes
        self._image_control.current_frame = self._current_frame

        # update the UI
        self._current_time.setText('{:10.3f}'.format(round(position / 1000 - self._start_trim, 3)))
        self._frame_box.setText('(frame: {:04})'.format(self.current_frame))

        # send event about frame change
        for callback in self.time_code_changed:
            callback(position / 1000 - self._start_trim)

    def _meta_data_changed_(self, available):
        if self._media_player.isMetaDataAvailable():
            resolution = self._media_player.metaData('Resolution')

            self._duration_time_code = self._media_player.metaData('Duration')   # get duration in ms
            self._fps = self._media_player.metaData('VideoFrameRate')  # get frames per second of the video
            self._media_player.setNotifyInterval(1000 / self._fps)
            self._frame_count = self._time_code_to_frame_number_(self._duration_time_code)  # get total video frames
            self._video_width = resolution.width()  # get width of the image
            self._video_height = resolution.height()  # get height of the image
            self.start_trim = 0  # no trimming when video is loaded
            self._start_frame = 0  # first frame is also the first frame of the video
            self._duration = self._duration_time_code / 1000
            self._end_frame = self._frame_count - 1  # don't trim the end of the video
            self.end_trim = self.duration  # use the duration of the video as trim mark (no trimming)

            # set maximum values of the ROI spin boxes
            self._box_roi_x.setMaximum(self._video_width)
            self._box_roi_width.setMaximum(self._video_width)
            self._box_roi_y.setMaximum(self._video_height)
            self._box_roi_height.setMaximum(self._video_height)

            # update the data on the UI elements
            self._total_time.setText('{:10.3f}'.format(self._end_trim - self._start_trim))
            self._frame_box.setText('(Frame: 0000)')
            self._timeline.setValue(0)
            self._timeline.setMaximum(self._duration_time_code)
            self._timeline.setEnabled(True)
            self._play_button.setEnabled(True)
            self._stop_button.setEnabled(True)
            self._next_frame_button.setEnabled(True)
            self._previous_frame_button.setEnabled(True)
            self.reset_roi()

            meta_data = dict()
            for key in self._media_player.availableMetaData():
                meta_data[key] = self._media_player.metaData(key)
            self.meta_data_loaded.emit(meta_data)

    def _frame_ready_(self, frame):
        if self._roi is not None:   # crop the frame to the ROI if one has been specified
            self._result_frame = frame.copy(self._roi)
        else:
            self._result_frame = frame
        self._image_control.set_image(self._result_frame)
        self._wait = False

        if self._media_player.position() > self.end_trim * 1000:
            self.pause()
            self._media_player.setPosition(self.end_trim * 1000)
        elif self._media_player.position() < self.start_trim * 1000:
            self.pause()
            self._media_player.setPosition(self.start_trim * 1000)

    def set_time(self, seconds):
        """
        Display the frame that is the closest to the given time
        :param seconds: time at which to display the frame in seconds
        """
        if not self.video_file_open:
            return
        self._media_player.setPosition(seconds * 1000)

    def get_time(self, frame_number):
        """
        Return the time code at the specified frame
        :param frame_number: frame number
        :return: time code in seconds
        """
        if not self.video_file_open:    # return zero if no file is opened
            return 0
        frame_number = self._clamp_frame_number_(frame_number)
        return frame_number / self.fps - self._start_trim

    @staticmethod
    def _to_numpy_array_(frame):
        channels = int(frame.byteCount() / frame.width() / frame.height())
        bits = frame.bits()
        bits.setsize(frame.byteCount())
        return np.frombuffer(bits, np.uint8).reshape(frame.height(), frame.width(), channels)

    def get_frame(self, frame_number, wait_for_new_frame=False):
        """
        Returns a numpy array containing the video frame at the given frame number
        :param frame_number: frame number
        :param wait_for_new_frame: Makes sure that a new frame is retrieved before it is returned (otherwise most recent is returned)
        :return: numpy array
        """
        if not self.video_file_open:    # return None if no video file is opened
            return None

        frame_number = self._clamp_frame_number_(frame_number)
        if wait_for_new_frame:
            self._wait = True
        old_interval = self._media_player.notifyInterval()
        self._media_player.setNotifyInterval(1)
        self._media_player.setPosition(self._frame_number_to_time_code(frame_number))
        while self._wait:
            sleep(0.001)
        self._media_player.setNotifyInterval(old_interval)

        result_frame = self._result_frame
        data = self._to_numpy_array_(result_frame)
        return data

    def _clamp_frame_number_(self, frame_number):
        """
        Clamps the given frame number to an allowed range
        :param frame_number: frame number
        :return: frame number between 0 and frame_count - 1
        """
        if frame_number < self._start_frame:
            frame_number = self._start_frame
        elif frame_number > self._end_frame:
            frame_number = self._end_frame
        return int(frame_number)

    def _clamp_time_code_(self, time_code):
        """
        Clamps the given time code to an allowed range
        :param time_code: time code (in ms)
        :return: time code (in ms)
        """
        if time_code < self._start_trim * 1000:
            time_code = self._start_trim * 1000
        elif time_code > self._end_trim * 1000:
            time_code = self._end_trim * 1000
        return time_code

    def set_roi(self, rect: QRect):
        """
        Sets the region of interest on the video footage.
        :param rect: rectangle representing the region of interest
        """
        self._roi = rect
        self._box_roi_x.setValue(rect.x())
        self._box_roi_y.setValue(rect.y())
        self._box_roi_width.setValue(rect.width())
        self._box_roi_height.setValue(rect.height())

        if self._frame_count > 0:
            self._display_time_code_(self._timeline.value())    # update the display

    def reset_roi(self):
        """
        Reset the region of interest
        """
        self._roi = None

        # set the full image as ROI on the spin boxes
        self._accept_roi_updates_from_boxes = False     # stop the spin boxes from updating the ROI
        self._box_roi_x.setValue(0)
        self._box_roi_y.setValue(0)
        self._box_roi_width.setValue(self._video_width)
        self._box_roi_height.setValue(self._video_height)
        self._accept_roi_updates_from_boxes = True      # re-enable the spin boxes to update the ROI

        if self._frame_count > 0:
            self._display_time_code_(self._timeline.value())

    def play(self):
        """
        Start playing the video that is currently loaded.
        """
        if self.is_playing:     # do nothing if the video is already playing
            return

        self._media_player.play()
        self._play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))  # set pause button icon to pause

    def pause(self):
        """
        Pauses the video.
        """
        self._media_player.pause()
        self._play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))   # set pause button icon to play

    def stop(self):
        """
        Stop the video and rewind.
        """
        self.pause()    # stop the video from playing
        self._media_player.setPosition(self.start_trim * 1000)  # return to the first frame

    def next_frame(self):
        """
        Skip one frame ahead.
        """
        if self.current_frame < self.end_frame:
            self.current_frame += 1

    def previous_frame(self):
        """
        Skip to the previous frame.
        """
        if self.current_frame > self.start_frame:
            self.current_frame -= 1

    def _play_pause_(self):
        """
        Play if the video is paused or pause if the video is currently playing.
        """
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def _display_time_code_(self, time_code):
        """
        Displays the requested time code on the widget.
        :param time_code: time code (in ms)
        """
        if not self.video_file_open:    # do nothing if no video file is open
            return

        time_code = self._clamp_time_code_(time_code)  # get proper time code
        self._media_player.setPosition(time_code)

    def _roi_box_value_changed_(self, *args):
        """
        Callback for changes made in the ROI spin boxes. Adjust the ROI accordingly.
        """
        if self._accept_roi_updates_from_boxes:
            roi_x = self._box_roi_x.value()
            roi_y = self._box_roi_y.value()
            roi_width = self._box_roi_width.value()
            roi_height = self._box_roi_height.value()
            self.set_roi(QRect(roi_x, roi_y, roi_width, roi_height))

    def close(self):
        """
        Closes the video file which is  currently opened.
        """
        if self._video_file_open:
            self._media_player.stop()
            self._frame_count = 0       # set the frame count to zero
            self._fps = 1               # set the frames per second to zero
            self._media_player.setPosition(0)              # set the timeline to zero
            self._timeline.setEnabled(False)        # disable the timeline
            self._play_button.setEnabled(False)     # disable the play button
            self._stop_button.setEnabled(False)     # disable the stop button
            self._next_frame_button.setEnabled(True)       # disable the skip frame button
            self._previous_frame_button.setEnabled(True)    # disable the previous frame button
            self._current_time.setText('0.000')     # set the current time code to zero
            self._total_time.setText('0.000')       # set the total time to zero
            self._frame_box.setText('(frame: 0000)')    # set the current frame to zero
            self._box_roi_x.setMaximum(0)       # set the ROI maximum to zero
            self._box_roi_width.setMaximum(0)   # set the ROI maximum to zero
            self._box_roi_y.setMaximum(0)       # set the ROI maximum to zero
            self._box_roi_height.setMaximum(0)  # set the ROI maximum to zero
            self.reset_roi()    # reset the ROI

    def _setup_(self):
        self._image_control = ImageRenderWidget()
        self._image_control.overlay_layers.append(self._selection_layer)
        self._layout.addWidget(self._image_control, 0, 0, 1, 10, Qt.AlignCenter)

        self._timeline = QJumpSlider(Qt.Horizontal)
        self._timeline.setEnabled(False)
        self._timeline.valueChangedSmart.connect(self._display_time_code_)
        self._layout.addWidget(self._timeline, 1, 4)

        self._current_time = QLabel('0.000')
        self._total_time = QLabel('0.000')
        self._frame_box = QLabel('(Frame: 0000)')
        self._layout.addWidget(self._current_time, 1, 5)
        self._layout.addWidget(QLabel('/'), 1, 6)
        self._layout.addWidget(self._total_time, 1, 7)
        self._layout.addWidget(QLabel(' s'), 1, 8)
        self._layout.addWidget(self._frame_box, 1, 9)

        self._play_button = QPushButton()
        self._play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self._play_button.setEnabled(False)
        self._play_button.clicked.connect(self._play_pause_)
        self._layout.addWidget(self._play_button, 1, 0)

        self._stop_button = QPushButton()
        self._stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self._stop_button.setEnabled(False)
        self._stop_button.clicked.connect(self.stop)
        self._layout.addWidget(self._stop_button, 1, 1)

        self._next_frame_button = QPushButton()
        self._next_frame_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self._next_frame_button.setEnabled(False)
        self._next_frame_button.clicked.connect(self.next_frame)
        self._layout.addWidget(self._next_frame_button, 1, 3)

        self._previous_frame_button = QPushButton()
        self._previous_frame_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self._previous_frame_button.setEnabled(False)
        self._previous_frame_button.clicked.connect(self.previous_frame)
        self._layout.addWidget(self._previous_frame_button, 1, 2)

        roi_frame = QFrame()
        roi_layout = QHBoxLayout()
        roi_frame.setLayout(roi_layout)
        roi_frame.setFixedHeight(38)
        roi_layout.addWidget(QLabel('ROI: ['))
        roi_layout.addWidget(QLabel('x:'))
        self._box_roi_x = QSpinBox()
        roi_layout.addWidget(self._box_roi_x)
        roi_layout.addWidget(QLabel('y:'))
        self._box_roi_y = QSpinBox()
        roi_layout.addWidget(self._box_roi_y)
        roi_layout.addWidget(QLabel('width:'))
        self._box_roi_width = QSpinBox()
        roi_layout.addWidget(self._box_roi_width)
        roi_layout.addWidget(QLabel('height:'))
        self._box_roi_height = QSpinBox()
        roi_layout.addWidget(self._box_roi_height)
        roi_layout.addWidget(QLabel(']'))
        roi_reset_button = QPushButton('Reset')
        roi_reset_button.clicked.connect(self.reset_roi)
        roi_layout.addWidget(roi_reset_button)
        self._box_roi_x.valueChanged.connect(self._roi_box_value_changed_)
        self._box_roi_y.valueChanged.connect(self._roi_box_value_changed_)
        self._box_roi_width.valueChanged.connect(self._roi_box_value_changed_)
        self._box_roi_height.valueChanged.connect(self._roi_box_value_changed_)
        self._layout.addWidget(roi_frame, 2, 0, 1, 9, Qt.AlignLeft)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.Qt import QApplication

    app = QApplication([])
    main = QMainWindow()
    video_editor = VideoEditor()
    #video_editor.load('Z:/shared/Master Thesis/Experiments/TrappingExperiment/Trapping_18.7.2019/power_walk_1W-350mW_1Bar.avi')
    main.setCentralWidget(video_editor)
    main.show()
    QApplication.instance().exec_()
