from QtModularUiPack.Widgets import EmptyFrame
from QtModularUiPack.Widgets.DataBinding import BindingEnabledWidget
from QtModularUiPack.ModularApplications.ToolFrameViewModels.experiment_frame_view_model import ExperimentViewModel, ExperimentOverviewViewModel
from PyQt5.QtWidgets import QGridLayout, QLabel, QComboBox, QPushButton, QMessageBox, QFrame, QScrollArea, QVBoxLayout, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


EXPERIMENT_CONFIG_FILE = 'experiment_settings.json'


class ExperimentFrame(EmptyFrame):
    """
    This frame allows the user to select from a list of experiments and run them
    """

    name = 'Experiment Control'

    @property
    def experiment_folder(self):
        return self.data_context.experiment_folder

    @experiment_folder.setter
    def experiment_folder(self, value):
        self.data_context.experiment_folder = value

    def __init__(self, parent=None, experiment_folder=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = ExperimentOverviewViewModel(experiment_folder=experiment_folder)
        self.data_context.add_experiment_request.connect(self._add_script_box_)
        self._scroll_layout = None
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self._layout)
        self._setup_()
        self.data_context.load_configuration()

    def _add_script_box_(self, cannot_be_removed=False):
        experiment_box = ExperimentBox(cannot_be_removed=cannot_be_removed, experiment_folder=self.experiment_folder)
        experiment_box.remove_request.append(self._remove_request_)
        self.data_context.experiments.append(experiment_box.data_context)
        self._scroll_layout.addWidget(experiment_box)

    def _remove_request_(self, experiment_box):
        self.data_context.experiments.remove(experiment_box.data_context)
        experiment_box.setParent(None)

    def _setup_(self):
        # set title
        title = QLabel(self.name)
        title.setFont(QFont('Arial', 10))
        self._layout.addWidget(title, 0, 0)

        scroll_area = QScrollArea()
        self._scroll_layout = QVBoxLayout()
        self._scroll_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        scroll_area.setLayout(self._scroll_layout)
        group_box = QGroupBox()
        group_box.setLayout(self._scroll_layout)
        scroll_area.setWidget(group_box)
        scroll_area.setWidgetResizable(True)
        self._layout.addWidget(scroll_area, 1, 0)
        if len(self.data_context.experiments) == 0:
            self._add_script_box_(cannot_be_removed=True)

        add_button = QPushButton('add')
        add_button.clicked.connect(self._add_script_box_)
        self._layout.addWidget(add_button, 2, 0)


class ExperimentBox(QFrame, BindingEnabledWidget):

    def __init__(self, cannot_be_removed=False, experiment_folder=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cannot_be_removed = cannot_be_removed
        self.remove_request = list()
        self.data_context = ExperimentViewModel(experiment_folder=experiment_folder)
        self.data_context.widget = self
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self._layout)
        self._setup_()

    def message(self, message, title):
        """
        Callback if a message box was requested in the running experiment
        :param message: message to show
        :param title: title of message box
        """
        self.data_context.dialog_open = True
        box = QMessageBox(QMessageBox.NoIcon, title, message, QMessageBox.Ok, self)
        box.exec_()
        self.data_context.dialog_open = False

    def question(self, message, title):
        """
        Callback if a question dialog (yes / no) was requested in the running experiment
        :param message: question
        :param title: title
        :return: true or false
        """
        self.data_context.dialog_open = True
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.data_context.dialog_answer = reply == QMessageBox.Yes
        self.data_context.dialog_open = False

    def remove(self):
        for callback in self.remove_request:
            callback(self)

    def _setup_(self):
        self._layout.addWidget(QLabel('procedure:'), 0, 0)
        experiment_box = QComboBox()
        experiment_box.addItems(self.data_context.available_experiments)
        self.bindings.set_binding('selected_experiment', experiment_box, 'setCurrentIndex')
        self._layout.addWidget(experiment_box, 0, 1)

        run_button = QPushButton()
        run_button.setFixedWidth(80)
        self.bindings.set_binding('run_button_text', run_button, 'setText')
        self.bindings.set_binding('allow_run', run_button, 'setEnabled')
        run_button.clicked.connect(self.data_context.run_stop_experiment)
        self._layout.addWidget(run_button, 1, 1)

        if not self._cannot_be_removed:
            remove_button = QPushButton('remove')
            remove_button.clicked.connect(self.remove)
            self._layout.addWidget(remove_button, 0, 2)


if __name__ == '__main__':
    ExperimentFrame.standalone_application()

