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

from PyQt5.QtWidgets import QFrame, QAction, QHBoxLayout, QMenuBar
from PyQt5.QtCore import pyqtSignal
from QtModularUiPack.Widgets import EmptyFrame
from QtModularUiPack.Widgets.utils import get_builtin_frames
from QtModularUiPack.ViewModels import BaseViewModel
from QtModularUiPack.Framework import ModuleManager
import traceback


TEXT_SPLIT_HORIZONTALLY = 'split horizontally'
TEXT_SPLIT_VERTICALLY = 'split vertically'
TEXT_REMOVE = 'remove'
TEXT_VIEW = 'View'


class ModularFrame(QFrame):
    """
    This widget can be used in modular frame hosts to be arranged with neighbours into a custom user interface.
    """

    on_split_horizontal = pyqtSignal(QFrame)
    on_split_vertical = pyqtSignal(QFrame)
    on_remove = pyqtSignal(QFrame)
    received_data_context = pyqtSignal(BaseViewModel)
    data_context_removed = pyqtSignal(BaseViewModel)

    @property
    def splitter_index(self):
        """
        Gets the index within a splitter. Returns -1 if not inside a splitter.
        """
        if self.splitter is None:
            return -1

        for i in range(self.splitter.count()):
            if self.splitter.widget(i) == self:
                return i
        return -1

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        try:
            self._set_view_(value)
        except Exception as e:
            print('unable to setup frame with "{}". Error: {}'.format(value, e))
            traceback.print_exc()
            self._name = None

    def __init__(self, parent, splitter=None, name='empty frame', frame_search_path=None, *args, **kwargs):
        super(ModularFrame, self).__init__(parent, *args, **kwargs)
        self.frame_search_path = frame_search_path
        self.splitter = splitter
        self._valid_frame_types = dict()
        self._setup_()
        self._name = None
        self.loaded_tool_frame = None
        self.name = name

    def destroyed(self, p_object=None):
        super().destroyed(p_object)

    def deleteLater(self):
        if self.loaded_tool_frame is not None and 'data_context_changed' in dir(self.loaded_tool_frame):
            self.loaded_tool_frame.data_context_changed.disconnect(self._on_data_context_changed_)
        super().deleteLater()

    def resizeEvent(self, *args, **kwargs):
        """
        If a resize event occurs reposition the frame edit button.
        """
        self._frame_menu_button.resize(28, 25)  # resize the button
        self._frame_menu_button.raise_()    # make sure the button always stays on top of the other widgets
        self._frame_menu_button.move(10, self.geometry().height() - 30)     # move the button to the proper position

    def _request_action_(self, q):
        """
        Callback for frame edit events such as split or remove.
        :param q: argument
        """
        action = q.text()   # get action from the button pressed
        if action == TEXT_SPLIT_HORIZONTALLY:
            self.on_split_horizontal.emit(self)
        elif action == TEXT_SPLIT_VERTICALLY:
            self.on_split_vertical.emit(self)
        elif action == TEXT_REMOVE:
            self.on_remove.emit(self)

    def _set_view_button_(self, q):
        self._set_view_(q.text())

    def _set_view_(self, name):
        """
        Sets the content of the frame to a specified control.
        :param name: argument
        """
        # stop listen for changes in the data context
        if self.loaded_tool_frame is not None and 'data_context_changed' in dir(self.loaded_tool_frame):
            self.loaded_tool_frame.data_context_changed.disconnect(self._on_data_context_changed_)

            # call destructor of the attached data context
            if hasattr(self.loaded_tool_frame.data_context, '__del__'):
                self.loaded_tool_frame.data_context.__del__()

            # propagate event that a data context is no longer in use
            self._on_data_context_removed_(self.loaded_tool_frame.data_context)

        while self.content.count():
            child = self.content.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.loaded_tool_frame = self._valid_frame_types[name](self)
        self.content.addWidget(self.loaded_tool_frame)
        self._frame_menu_button.raise_()
        self._name = name

        # start listen for changes in the data context so that it can be relayed
        if self.loaded_tool_frame is not None and 'data_context_changed' in dir(self.loaded_tool_frame):
            self.loaded_tool_frame.data_context_changed.connect(self._on_data_context_changed_)

            if self.loaded_tool_frame.data_context is not None:
                self._on_data_context_changed_(self.loaded_tool_frame.data_context)

    def _on_data_context_removed_(self, data_context):
        if data_context is not None:
            self.data_context_removed.emit(data_context)

    def _on_data_context_changed_(self, data_context):
        self.received_data_context.emit(data_context)

    def get_possible_frames(self):
        """
        Get available frames for the modular frame to display.
        """
        # clear existing frame types
        self._valid_frame_types.clear()
        self._view_menu.clear()

        # get classes
        frame_classes = get_builtin_frames()
        if self.frame_search_path is not None:
            additional = ModuleManager.instance.load_classes_from_folder_derived_from(self.frame_search_path, EmptyFrame)
            frame_classes += additional

        for cls in frame_classes:
            name = cls.name
            i = 1
            already_present = True
            while already_present:  # make sure that there are no duplicate names
                already_present = name in self._valid_frame_types
                if already_present and name != 'empty frame':
                    name = '{} ({})'.format(cls.name, i)
                    i += 1
                else:
                    break
            if not already_present:
                self._valid_frame_types[name] = cls
                self._view_menu.addAction(name)
        if '_name' in dir(self):
            self.name = self._name  # reload current frame

    def _setup_(self):
        """
        Setup the frame with its frame edit button.
        """
        self._frame_menu_button = QMenuBar(self)    # add the menu bar
        self.content = QHBoxLayout(self)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.content)
        menu = self._frame_menu_button.addMenu('...')   # add the button
        menu.addAction(TEXT_SPLIT_HORIZONTALLY)        # add the action to split horizontally
        menu.addAction(TEXT_SPLIT_VERTICALLY)          # add the action to split vertically
        menu.addAction(TEXT_REMOVE)                    # add the action to remove
        self._view_menu = menu.addMenu(TEXT_VIEW)
        self.get_possible_frames()
        menu.triggered[QAction].connect(self._request_action_)   # connect the events
        self._view_menu.triggered[QAction].connect(self._set_view_button_)
        self._frame_menu_button.raise_()    # make sure the button is above all other widgets
