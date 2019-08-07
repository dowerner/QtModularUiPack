from PyQt5.QtWidgets import QHBoxLayout
from ViewModels import BaseContextAwareViewModel, ModularApplicationViewModel
from Widgets import ModularFrameHost, EmptyFrame
from Framework.ImportTools.utils import is_non_strict_type, is_non_strict_subclass


class MainWindow(EmptyFrame):
    """
    This is the main window of the Lab Master application
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_context = ModularApplicationViewModel()
        self._layout = QHBoxLayout()
        self.setLayout(self._layout)

        # content
        self._frame_host = ModularFrameHost(self)
        self._frame_host.data_context_received.connect(self._on_child_data_context_received_)
        self._frame_host.data_context_removed.connect(self._on_child_data_context_removed_)
        self._layout.addWidget(self._frame_host)

    def _on_child_data_context_received_(self, tool_frame, child_data_context):
        """
        Callback for handling new data contexts that have been added in the tool frame section
        :param tool_frame: tool frame that caused the event
        :param child_data_context: data context that was added
        :return:
        """
        self.data_context.other_data_contexts.append(child_data_context)

        if is_non_strict_subclass(type(child_data_context), BaseContextAwareViewModel):
            self.data_context.connect_context_aware_view_model(child_data_context)

    def _on_child_data_context_removed_(self, child_data_context):
        """
        Callback for handling new data contexts that have been removed in the tool frame section
        :param child_data_context: data context that was removed
        :return:
        """
        if child_data_context in self._vm.other_data_contexts:
            self.data_context.other_data_contexts.remove(child_data_context)

        if is_non_strict_type(type(child_data_context), BaseContextAwareViewModel):
            self.data_context.disconnect_context_aware_view_model(child_data_context)

    def load_settings(self, path):
        self._frame_host.load(path)

    def closeEvent(self, *args, **kwargs):
        self._frame_host.save(self._vm.frame_save_path)
        self.data_context.save_configuration()   # save configuration on close
