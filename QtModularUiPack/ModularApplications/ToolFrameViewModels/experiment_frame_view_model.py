from QtModularUiPack.ViewModels import BaseContextAwareViewModel
from QtModularUiPack.Framework import KillableThread, ModuleManager, ObservableList, is_non_strict_type, Signal
from QtModularUiPack.Framework.Experiments import BaseExperiment
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot, QObject
import json
import os


EXPERIMENT_CONFIG = 'experiment_config.json'


class ExperimentOverviewViewModel(BaseContextAwareViewModel):

    name = 'experiments'

    add_experiment_request = Signal(bool)

    @property
    def experiment_folder(self):
        return self._experiment_folder

    @experiment_folder.setter
    def experiment_folder(self, value):
        self._experiment_folder = value
        self.experiments.clear()
        self.add_experiment(True)

    def __init__(self, experiment_folder=None):
        super().__init__()
        self.experiments = ObservableList()
        self.experiments.item_added.connect(self._experiment_added_)
        self._experiment_folder = experiment_folder
        self.data_context_changed.connect(self._data_contexts_changed_)
        self.other_data_contexts.item_added.connect(self._data_contexts_changed_)
        self.other_data_contexts.item_removed.connect(self._data_contexts_changed_)

    def add_experiment(self, cannot_be_removed=False):
        self.add_experiment_request.emit(cannot_be_removed)

    def save_configuration(self):
        experiment_list = list()
        for experiment in self.experiments:
            experiment_data = {'experiment_name': experiment.experiment_name}
            experiment_list.append(experiment_data)

        data = {'experiments': experiment_list, 'experiment_folder': self.experiment_folder}
        with open(EXPERIMENT_CONFIG, 'w') as file:
            file.write(json.dumps(data))

    def load_configuration(self):
        if os.path.isfile(EXPERIMENT_CONFIG):
            with open(EXPERIMENT_CONFIG, 'r') as file:
                data = json.loads(file.read())
                self.experiment_folder = data['experiment_folder']
                while len(self.experiments) < len(data['experiments']):
                    self.add_experiment(cannot_be_removed=len(self.experiments) == 0)

                for i in range(len(self.experiments)):
                    experiment_name = data['experiments'][i]['experiment_name']
                    if experiment_name in self.experiments[i].available_experiments:
                        index = self.experiments[i].available_experiments.index(experiment_name)
                        self.experiments[i].selected_experiment = index
        if self.experiment_folder is None:
            path = QFileDialog.getExistingDirectory(None, "Select folder containing experiment scripts");
            if path != '':
                self.experiment_folder = path

    def _data_contexts_changed_(self, vm):
        for experiment in self.experiments:
            experiment.other_data_contexts = self.other_data_contexts

    def _experiment_added_(self, experiment: BaseContextAwareViewModel):
        experiment.other_data_contexts = self.other_data_contexts


class ExperimentViewModel(QObject, BaseContextAwareViewModel):
    """
    This view model provides the data context for the Experiment Frame
    """

    name = 'experiment'

    @property
    def experiment_name(self):
        if self._experiment is not None:
            return self._experiment.name
        else:
            return None

    @property
    def allow_run(self):
        """
        True if a valid experiment is present that can be executed.
        """
        return self._experiment is not None

    @property
    def run_button_text(self):
        """
        Gets the text of the start stop button on the UI
        """
        if self._running:
            return 'stop'
        else:
            return 'run'

    @property
    def selected_experiment(self):
        """
        Index of selected experiment in the list.
        """
        return self._selected_experiment

    @selected_experiment.setter
    def selected_experiment(self, value):
        """
        Sets the experiment index
        """
        self._selected_experiment = value
        self._experiment = self.experiments[value]
        self.notify_change('selected_experiment')
        self.notify_change('allow_run')

    @property
    def available_experiments(self):
        """
        Gets a list of all available experiments
        """
        return [experiment.name for experiment in self.experiments]

    def __init__(self, experiment_folder=None):
        super().__init__()

        # folder to look for experiments
        self.experiment_folder = experiment_folder

        self._tool_frame_data_contexts = None
        self.widget = None
        self._experiment = None
        self._running = False
        self._selected_experiment = -1
        self.experiments = list()
        self._look_for_experiments_()
        self._experiment_thread = None
        self.dialog_open = False
        self.dialog_answer = False

        # initialize tools
        self._tools = self.data_context_container

    def __del__(self):
        if self._running:
            self.run_stop_experiment()

    def run_stop_experiment(self):
        """
        Runs or stops the selected experiment
        """
        if not self._running:
            self.run()
        else:
            self.stop()

    def run(self):
        """
        Runs the selected experiment
        :return:
        """
        if not self._running:
            self._experiment_thread = KillableThread(target=self._experiment_worker_)
            self._experiment_thread.start()

    def stop(self):
        """
        Stops the currently running experiment
        """
        if self._experiment_thread is not None:
                self._experiment_thread.terminate()
                self._experiment_thread = None
                self._running = False
                self.notify_change('allow_run')
                self.notify_change('run_button_text')

    @pyqtSlot(str, str)
    def message(self, message, title=None):
        """
        Callback if a message box was requested during an experiment
        :param message: message
        :param title: title
        """
        self.widget.message(message, title)

    @pyqtSlot(str, str)
    def question(self, message, title=None):
        """
        Callback if a question dialog was requested during an experiment
        :param message: question
        :param title: title
        """
        self.widget.question(message, title)

    def _experiment_worker_(self, *args):
        """
        Thread worker that initializes and runs the experiment (meant to be run in separate thread)
        """
        instance = self._experiment(self._tools)    # create experiment
        instance.calling_context = self     # use dependency injection to give experiment access to all tools
        self._running = True    # signal the start of the experiment
        self.notify_change('allow_run')
        self.notify_change('run_button_text')
        instance.run()  # run the experiment
        self._running = False   # signal the close of the experiment
        self.notify_change('allow_run')
        self.notify_change('run_button_text')

    def _look_for_experiments_(self):
        """
        Look for experiments in a given folder (Experiments have to be of type BaseExperiment)
        :return:
        """
        if self.experiment_folder is None:
            return
        path = self.experiment_folder
        experiment_classes = ModuleManager.instance.load_classes_from_folder_derived_from(path, BaseExperiment)

        for cls in experiment_classes:
            if is_non_strict_type(cls, BaseExperiment):     # do not add BaseExperiment
                continue
            self.experiments.append(cls)
