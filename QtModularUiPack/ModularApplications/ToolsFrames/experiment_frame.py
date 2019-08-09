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

from QtModularUiPack.Widgets import EmptyFrame
from QtModularUiPack.Widgets.DataBinding import BindingEnabledWidget
from QtModularUiPack.ModularApplications.ToolFrameViewModels.experiment_frame_view_model import ExperimentViewModel, ExperimentOverviewViewModel
from PyQt5.QtWidgets import QGridLayout, QLabel, QComboBox, QPushButton, QMessageBox, QFrame, QScrollArea, QVBoxLayout, QGroupBox, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal


EXPERIMENT_CONFIG_FILE = 'experiment_settings.json'


class ExperimentFrame(EmptyFrame):
    """
    This frame allows the user to select from a list of experiments and run them
    """

    name = 'Experiment Control'

    @property
    def experiment_folder(self):
        """
        Gets the folder containing the experiments as python scripts
        """
        return self.data_context.experiment_folder

    @experiment_folder.setter
    def experiment_folder(self, value):
        """
        Sets the folder that should be searched for python scripts based on BaseExperiment
        :param value: path
        """
        self.data_context.experiment_folder = value

    def __init__(self, parent=None, experiment_folder=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_context = ExperimentOverviewViewModel(experiment_folder=experiment_folder)
        self.data_context.add_experiment_request.connect(self._add_script_box_)     # listen for experiment add request
        self._scroll_layout = None      # create variable for scroll view
        self._layout = QGridLayout()    # create grid layout
        self._layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)   # set top-left alignment within the main grid
        self.setLayout(self._layout)
        self._setup_()
        self.data_context.load_configuration()      # load saved configuration

    def _add_script_box_(self, cannot_be_removed=False):
        """
        Add experiment box widget to scroll view
        :param cannot_be_removed: If true there will be no remove button in the experiment box
        """
        experiment_box = ExperimentBox(cannot_be_removed=cannot_be_removed, experiment_folder=self.experiment_folder)
        experiment_box.remove_requested.connect(self._remove_request_)  # listen for remove request from the box
        self.data_context.experiments.append(experiment_box.data_context)   # add the experiment to the overview data context
        self._scroll_layout.addWidget(experiment_box)   # add the box to the scroll view

    def _remove_request_(self, experiment_box):
        """
        Callback for the remove button on the experiment box
        :param experiment_box: box which triggered the signal
        """
        self.data_context.experiments.remove(experiment_box.data_context)   # remove data context
        experiment_box.setParent(None)  # remove widget

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

        control_frame = QFrame()
        control_layout = QHBoxLayout()
        control_frame.setLayout(control_layout)
        add_button = QPushButton('add')
        add_button.setFixedWidth(100)
        add_button.clicked.connect(self._add_script_box_)
        control_layout.addWidget(add_button)

        add_button = QPushButton('change experiment folder...')
        add_button.setFixedWidth(200)
        add_button.clicked.connect(self.data_context.change_experiment_folder)
        control_layout.addWidget(add_button)
        self._layout.addWidget(control_frame, 2, 0, 1, 1, Qt.AlignRight)


class ExperimentBox(QFrame, BindingEnabledWidget):
    """
    This widget is the visual representation of an experiment box on the experiment frame
    """

    remove_requested = pyqtSignal(object)

    def __init__(self, cannot_be_removed=False, experiment_folder=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cannot_be_removed = cannot_be_removed
        self._experiment_selection = None
        self.data_context = ExperimentViewModel(experiment_folder=experiment_folder)    # add data context for the box
        self.data_context.property_changed.connect(self._property_changed_)     # listen to property changes
        self.data_context.widget = self     # dependency-injection
        self._layout = QGridLayout()
        self._layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self._layout)
        self._setup_()

    def _property_changed_(self, name):
        if name == 'available_experiments':     # update collection of available experiments on the UI
            # retrieve currently selected experiment
            experiment_name = self._experiment_selection.itemText(self.data_context.selected_experiment)

            # remove all experiments from the list and add the new ones
            self._experiment_selection.clear()
            self._experiment_selection.addItems(self.data_context.available_experiments)

            # check if the selected experiment is still present and select it if possible
            idx = self._experiment_selection.findText(experiment_name)
            if idx != -1:
                self.data_context.selected_experiment = idx

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
        """
        Remove the experiment box
        """
        self.remove_requested.emit(self)

    def _setup_(self):
        # draw selection area
        self._layout.addWidget(QLabel('procedure:'), 0, 0)
        self._experiment_selection = QComboBox()
        self._experiment_selection.addItems(self.data_context.available_experiments)
        self.bindings.set_binding('selected_experiment', self._experiment_selection, 'setCurrentIndex')
        self._layout.addWidget(self._experiment_selection, 0, 1)

        # draw control area
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

