from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QSplitter, QFrame, QMenuBar, QGroupBox, QLabel, QDoubleSpinBox, QRadioButton
from QtModularUiPack.Widgets import EmptyFrame, VideoEditor, PyGraphWidget, CodeEditor
from QtModularUiPack.Widgets.QtExtensions import QDoubleRangeSlider, QDoubleSlider
from QtModularUiPack.ModularApplications.ToolFrameViewModels.video_analyzer_view_model import VideoAnalyzerViewModel, DATA_MODE_TRACE, DATA_MODE_SPECTROGRAM
from PyQt5.QtCore import Qt, QSize


SPINBOX_DECIMALS = 6


class VideoAnalyzerFrame(EmptyFrame):

    name = 'Video Analyzer'

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = VideoAnalyzerViewModel()
        self.data_context.property_changed.connect(self._property_changed_)
        self.data_context.set_ui_host(self)
        self._layout = QGridLayout()
        self.setLayout(self._layout)
        self._update_plot_time = True
        self._update_video_time = True
        self._update_result_time = True
        self._setup_()

    def _property_changed_(self, name):
        if name == 'plot_data' or (name == 'data_mode' and self.data_context.data_mode == DATA_MODE_TRACE and self.data_context.plot_data[0] is not None):
            self.plot.set_data(*self.data_context.plot_data, self.data_context.auto_fit_plot_data)
            #self.plot.x_label ='time [s]'
            #self.plot.y_label = 'voltage [V]'
            self.title = 'signal'
        elif name == 'spectrogram' and self.data_context.data_mode == DATA_MODE_SPECTROGRAM:
            self.plot.set_imshow(self.data_context.spectrogram, extent=self.data_context.spectrogram_range)
            #self.plot.x_label = 'time [s]'
            #self.plot.y_label = 'power/frequency [dB/kHz]'
            self.title = 'Spectrogram'
        elif name == 'video_path':
            self.video_editor.load(self.data_context.video_path)
        elif name == 'video_time_boundary_lower':
            self.video_editor.start_trim = self.data_context.video_time_boundary_lower
        elif name == 'video_time_boundary_upper':
            self.video_editor.end_trim = self.data_context.video_time_boundary_upper
        elif name == 'current_time':
            self._update_video_time = False
            self._update_plot_time = False
            self._update_result_time = False
            self.video_editor.set_time(self.data_context.current_time)
            self.plot.x_indicator_position = self.data_context.current_time
            self.result_plot.x_indicator_position = self.data_context.current_time
            self._update_video_time = True
            self._update_plot_time = True
            self._update_result_time = True
        elif name == 'result_plot_data':
            self.result_plot.set_data(*self.data_context.result_plot_data)

    def _plot_time_changed_(self, seconds):
        if not self._update_plot_time:
            return
        self._update_video_time = False
        self._update_result_time = False
        self.video_editor.set_time(seconds)
        self.data_context.set_time_silent(seconds)
        self.result_plot.x_indicator_position = seconds
        self._update_video_time = True
        self._update_result_time = True

    def _result_time_changed_(self, seconds):
        if not self._update_result_time:
            return
        self._update_plot_time = False
        self._update_result_time = False
        self.video_editor.set_time(seconds)
        self.data_context.set_time_silent(seconds)
        self._update_plot_time = True
        self._update_result_time = True

    def _video_time_changed_(self, seconds):
        if not self._update_video_time:
            return
        self._update_result_time = False
        self._update_plot_time = False
        self.plot.x_indicator_position = seconds
        self.data_context.set_time_silent(seconds)
        self.result_plot.x_indicator_position = seconds
        self._update_plot_time = True
        self._update_result_time = True

    def _video_meta_data_ready_(self, meta_data):
        self.data_context.video_duration = self.video_editor.duration
        self.data_context.video_time_boundary_upper = self.video_editor.duration
        self.data_context.video_time_boundary_lower = 0
        self.data_context.video_delta_time = 1 / self.video_editor.fps

    def _setup_(self):
        menu_bar = self.add_widget(QMenuBar(), 'ui_enabled', 'setEnabled')
        file_menu = menu_bar.addMenu('File')
        action_import_video = menu_bar.addAction('Import Video')
        action_import_video.triggered.connect(self.data_context.import_video)
        action_import_data = menu_bar.addAction('Import PD Trace')
        action_import_data.triggered.connect(self.data_context.import_data)
        action_open_data = file_menu.addAction('Open')
        action_open_data.triggered.connect(self.data_context.open)
        action_save_data = file_menu.addAction('Save')
        action_save_data.triggered.connect(self.data_context.save)
        action_save_data = file_menu.addAction('Save As')
        action_save_data.triggered.connect(self.data_context.save_as)
        action_export_video = file_menu.addAction('Export Combined Video')
        action_export_video.triggered.connect(self.data_context.export_video)
        action_export_result_plot = file_menu.addAction('Export Result Plot')
        action_export_result_plot.triggered.connect(self.data_context.export_result_plot)
        self._layout.addWidget(menu_bar, 0, 0)

        main_splitter = QSplitter(Qt.Horizontal)

        editor_frame = QFrame()
        editor_layout = QVBoxLayout()
        editor_frame.setLayout(editor_layout)

        editor_splitter = QSplitter(Qt.Vertical)
        editor_layout.addWidget(editor_splitter)

        self.video_editor = VideoEditor()
        self.video_editor.meta_data_loaded.connect(self._video_meta_data_ready_)
        self.data_context.video_editor = self.video_editor
        self.video_editor.overlay_layers.append(self.data_context.video_overlay)
        self.video_editor.time_code_changed.append(self._video_time_changed_)
        self.video_editor.setFrameShape(QFrame.StyledPanel)
        self.plot = PyGraphWidget(title='signal', x_label='time [s]', y_label='value')
        self.plot.set_matplotlib_default_style()
        self.plot.show_x_position_indicator = True
        self.plot.x_indicator_label = 'time'
        self.plot.x_position_indicator_changed.connect(self._plot_time_changed_)
        self.plot.setFrameShape(QFrame.StyledPanel)

        self.result_plot = PyGraphWidget(title='Image Processing Result', x_label='time [s]', y_label='value')
        self.result_plot.set_matplotlib_default_style()
        self.result_plot.show_x_position_indicator = True
        self.result_plot.x_indicator_label = 'time'
        self.result_plot.x_position_indicator_changed.connect(self._result_time_changed_)
        self.result_plot.setFrameShape(QFrame.StyledPanel)

        video_result_plot_splitter = QSplitter(Qt.Horizontal)
        editor_splitter.addWidget(self.plot)
        editor_splitter.addWidget(video_result_plot_splitter)
        video_result_plot_splitter.addWidget(self.video_editor)
        video_result_plot_splitter.addWidget(self.result_plot)

        tools_frame = self.add_widget(QFrame(), 'ui_enabled', 'setEnabled')
        tools_layout = QVBoxLayout()
        tools_frame.setLayout(tools_layout)
        tools_splitter = QSplitter(Qt.Vertical)
        tools_splitter.addWidget(tools_frame)
        main_splitter.addWidget(tools_splitter)
        main_splitter.addWidget(editor_frame)
        self._layout.addWidget(main_splitter, 1, 0)

        plot_box = QGroupBox('Plot Options')
        plot_box_layout = QGridLayout()
        plot_box_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        plot_box.setLayout(plot_box_layout)
        plot_box_layout.addWidget(QLabel('Time Range:'), 0, 0)
        plot_range_slider = QDoubleRangeSlider()
        plot_range_slider.setFixedSize(QSize(120, 18))
        self.bindings.set_binding('plot_start', plot_range_slider, 'setMin')
        self.bindings.set_binding('plot_time_boundary_lower', plot_range_slider, 'setStart')
        self.bindings.set_binding('plot_time_boundary_upper', plot_range_slider, 'setEnd')
        self.bindings.set_binding('plot_duration', plot_range_slider, 'setMax')
        self.bindings.set_binding('plot_delta_time', plot_range_slider, 'setIncrement')
        plot_box_layout.addWidget(QLabel('lower:'), 0, 2)
        plot_lower_bound_box = self.add_widget(QDoubleSpinBox(decimals=SPINBOX_DECIMALS), 'plot_time_boundary_lower',
                                               'setValue')
        self.bindings.set_binding('plot_time_boundary_upper', plot_lower_bound_box, 'setMaximum')
        self.bindings.set_binding('plot_start', plot_lower_bound_box, 'setMinimum')
        self.bindings.set_binding('plot_delta_time', plot_lower_bound_box, 'setSingleStep')
        plot_box_layout.addWidget(plot_lower_bound_box, 0, 3)
        plot_box_layout.addWidget(QLabel('upper:'), 0, 4)
        plot_upper_bound_box = self.add_widget(QDoubleSpinBox(decimals=SPINBOX_DECIMALS), 'plot_time_boundary_upper',
                                               'setValue')
        self.bindings.set_binding('plot_time_boundary_lower', plot_upper_bound_box, 'setMinimum')
        self.bindings.set_binding('plot_duration', plot_upper_bound_box, 'setMaximum')
        self.bindings.set_binding('plot_delta_time', plot_upper_bound_box, 'setSingleStep')
        plot_box_layout.addWidget(plot_upper_bound_box, 0, 5)
        plot_box_layout.addWidget(plot_range_slider, 0, 1)
        plot_box_layout.addWidget(QLabel('Temporal Offset:'), 1, 0)
        plot_temporal_slider = self.add_widget(QDoubleSlider(), 'plot_temporal_offset', 'setValue', width=120)
        self.bindings.set_binding('plot_duration', plot_temporal_slider, 'setMinimum', operation=lambda x: -x)
        self.bindings.set_binding('plot_duration', plot_temporal_slider, 'setMaximum')
        self.bindings.set_binding('plot_delta_time', plot_temporal_slider, 'setIncrement')
        plot_box_layout.addWidget(plot_temporal_slider, 1, 1, 1, 2, Qt.AlignLeft)
        plot_temporal_offset_box = self.add_widget(QDoubleSpinBox(decimals=SPINBOX_DECIMALS), 'plot_temporal_offset',
                                                   'setValue')
        self.bindings.set_binding('plot_delta_time', plot_temporal_offset_box, 'setSingleStep')
        self.bindings.set_binding('plot_duration', plot_temporal_offset_box, 'setMinimum', operation=lambda x: -x)
        self.bindings.set_binding('plot_duration', plot_temporal_offset_box, 'setMaximum')
        plot_box_layout.addWidget(plot_temporal_offset_box, 1, 3)
        show_time_trace_radio = QRadioButton('time trace')
        show_spectrogram_radio = QRadioButton('spectrogram')
        self.bindings.set_binding('data_mode', show_time_trace_radio, 'setChecked',
                                  operation=lambda x: x == DATA_MODE_TRACE,
                                  inv_op=lambda x: DATA_MODE_TRACE if x else DATA_MODE_SPECTROGRAM)
        self.bindings.set_binding('data_mode', show_spectrogram_radio, 'setChecked',
                                  operation=lambda x: x == DATA_MODE_SPECTROGRAM,
                                  inv_op=lambda x: DATA_MODE_SPECTROGRAM if x else DATA_MODE_TRACE)
        plot_box_layout.addWidget(show_time_trace_radio, 2, 0)
        plot_box_layout.addWidget(show_spectrogram_radio, 2, 1)
        tools_layout.addWidget(plot_box)

        video_box = QGroupBox('Video Options')
        video_box_layout = QGridLayout()
        video_box_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        video_box.setLayout(video_box_layout)
        video_box_layout.addWidget(QLabel('Time Range:'), 0, 0)
        video_range_slider = QDoubleRangeSlider()
        video_range_slider.setFixedSize(QSize(120, 18))
        self.bindings.set_binding('video_time_boundary_lower', video_range_slider, 'setStart')
        self.bindings.set_binding('video_time_boundary_upper', video_range_slider, 'setEnd')
        self.bindings.set_binding('video_duration', video_range_slider, 'setMax')
        self.bindings.set_binding('video_delta_time', video_range_slider, 'setIncrement')
        video_box_layout.addWidget(QLabel('lower:'), 0, 2)
        video_lower_bound_box = self.add_widget(QDoubleSpinBox(decimals=SPINBOX_DECIMALS), 'video_time_boundary_lower',
                                                'setValue')
        self.bindings.set_binding('video_time_boundary_upper', video_lower_bound_box, 'setMaximum')
        self.bindings.set_binding('video_start', video_lower_bound_box, 'setMinimum')
        self.bindings.set_binding('video_delta_time', video_lower_bound_box, 'setSingleStep')
        video_box_layout.addWidget(video_lower_bound_box, 0, 3)
        video_box_layout.addWidget(QLabel('upper:'), 0, 4)
        video_upper_bound_box = self.add_widget(QDoubleSpinBox(decimals=SPINBOX_DECIMALS), 'video_time_boundary_upper',
                                                'setValue')
        self.bindings.set_binding('video_time_boundary_lower', video_upper_bound_box, 'setMinimum')
        self.bindings.set_binding('video_duration', video_upper_bound_box, 'setMaximum')
        self.bindings.set_binding('video_delta_time', video_upper_bound_box, 'setSingleStep')
        video_box_layout.addWidget(video_upper_bound_box, 0, 5)
        video_box_layout.addWidget(video_range_slider, 0, 1)
        tools_layout.addWidget(video_box)

        code_editor_frame = QFrame()
        code_editor_layout = QGridLayout()
        code_editor_frame.setLayout(code_editor_layout)
        import_code_splitter = QSplitter(Qt.Vertical)
        code_menu_bar = self.add_widget(QMenuBar(), 'ui_enabled', 'setEnabled')
        run_code_on_current_action = code_menu_bar.addAction('run on current frame')
        run_code_on_current_action.triggered.connect(self.data_context.run_on_current_frame)
        run_code_on_entire_action = code_menu_bar.addAction('run on entire clip')
        run_code_on_entire_action.triggered.connect(self.data_context.run_on_entire_clip)
        code_editor_layout.addWidget(code_menu_bar, 0, 0)
        code_editor_layout.addWidget(import_code_splitter, 1, 0)
        import_editor_box = QGroupBox('Single Run/Import Code')
        import_editor_box_layout = QVBoxLayout()
        import_editor_box.setLayout(import_editor_box_layout)
        import_editor = self.add_widget(CodeEditor(), 'import_editor_code', 'setText')
        import_editor_box_layout.addWidget(import_editor)
        import_code_splitter.addWidget(import_editor_box)
        code_editor_box = QGroupBox('Image Processing Code')
        code_editor_box_layout = QVBoxLayout()
        code_editor_box.setLayout(code_editor_box_layout)
        code_editor = self.add_widget(CodeEditor(), 'frame_editor_code', 'setText')
        code_editor_box_layout.addWidget(code_editor)
        import_code_splitter.addWidget(code_editor_box)
        import_code_splitter.setSizes([20, 200])
        tools_splitter.addWidget(code_editor_frame)


if __name__ == '__main__':
    VideoAnalyzerFrame.standalone_application()
