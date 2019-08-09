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

from PyQt5.QtWidgets import QSplitter, QStackedWidget, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from QtModularUiPack.Widgets import ModularFrame
from QtModularUiPack.ViewModels import BaseViewModel
from QtModularUiPack.Framework import ModuleManager
import json
import os


class ModularFrameHost(QStackedWidget):
    """
    This widget can be used to add and remove modular frames at will. The widgets state can be saved to json.
    """

    data_context_received = pyqtSignal(BaseViewModel)
    data_context_removed = pyqtSignal(BaseViewModel)

    @property
    def frame_search_path(self):
        """
        Gets the path where the host looks for tool frames which can be displayed
        :return: path
        """
        return self._frame_search_path

    @frame_search_path.setter
    def frame_search_path(self, value):
        """
        Sets the path where the host looks for tool frames which can eb displayed
        :param value: path
        """
        self._frame_search_path = value
        for frame in self._modular_frames:
            frame.frame_search_path = value

    @property
    def is_restoring(self):
        """
        True if the host is currently restoring frames
        """
        return self._is_restoring

    def __init__(self, parent, frame_search_path=None, *args, **kwargs):
        super(ModularFrameHost, self).__init__(parent, *args, **kwargs)
        self._frame_search_path = frame_search_path
        self._base_splitter = None
        self._is_restoring = False
        self._setup_frame_host_()

    def save(self, path):
        """
        Saves the widgets state to json.
        :param path: file path
        """
        data = self._get_data_recursive_(self._base_splitter)   # retrieve dictionary representing the frame hierarchy
        json_data = json.dumps(data, indent=1)  # generate json string
        with open(path, 'w') as file:
            file.write(json_data)   # write json string to file

    def load(self, path):
        """
        Restores all frames according to the saved state from the given json file.
        :param path: file path
        """
        if not os.path.isfile(path):    # do noting if the given file does not exist
            return

        self._is_restoring = True
        with open(path, 'r') as file:
            data = json.loads(file.read())  # retrieve dictionary representing the frame hierarchy from json file

            self._modular_frames[0].deleteLater()   # delete the initial frame
            self._modular_frames.clear()    # remove initial frame from list
            self._base_splitter.deleteLater()   # delete initial splitter
            self._restore_frames_recursive_(data, self)     # restore the widget state based on the loaded data
        self._is_restoring = False

    def reload_possible_frames(self):
        """
        Re-imports all possible tool frame classes which can be used in the modular frames.
        """
        ModuleManager.instance.reload_modules()
        for frame in self._modular_frames:
            frame.get_possible_frames()

    def split_frame(self, frame, orientation):
        """
        Split the given frame either horizontally or vertically.
        :param frame: frame to split
        :param orientation: orientation along which the frame will be split
        """
        opposite_orientation = Qt.Vertical if orientation == Qt.Horizontal else Qt.Horizontal   # get opposite orientation
        parent_splitter = frame.splitter    # get reference to the splitter wherein the frame is embedded (maybe none)
        splitter = None     # variable to hold the splitter that will be used to embed this frame after splitting

        # if the frame is not embedded in a splitter or the orientation of the embedding splitter does not match a new splitter has to be created
        if parent_splitter is None or parent_splitter.orientation() == opposite_orientation:
            splitter = QSplitter(orientation)   # create new splitter

            if parent_splitter is None:     # if the frame was not embedded into a splitter the new splitter is the base splitter
                self.addWidget(splitter)
                self._base_splitter = splitter
                splitter.addWidget(frame)
            else:  # if the frame was embedded into a differently oriented splitter, the new splitter will take its place
                splitter_index = frame.splitter_index   # get the correct position of the new splitter within the parent splitter

                # get the sizes of all the widgets within the parent splitter
                if orientation == Qt.Horizontal:
                    sizes = [parent_splitter.widget(i).geometry().height() for i in range(parent_splitter.count())]
                else:
                    sizes = [parent_splitter.widget(i).geometry().width() for i in range(parent_splitter.count())]

                splitter.addWidget(frame)   # add the frame to the new splitter
                parent_splitter.insertWidget(splitter_index, splitter)  # add the splitter to the parent splitter
                parent_splitter.setSizes(sizes)     # restore the dimensions of the widgets within the parent splitter

            frame.splitter = splitter   # store the reference to the newly created splitter within the frame
        elif parent_splitter.orientation() == orientation:
            splitter = parent_splitter  # if the orientation of the existing splitter matches just use it to proceed

        # store the sizes of all the existing widgets in the splitter
        # half the size of the frame to be split and add an additional size which is also half of the frames current dimension
        geometry = frame.geometry()
        if orientation == Qt.Horizontal:
            sizes = [splitter.widget(i).geometry().height() for i in range(splitter.count())]
            sizes[frame.splitter_index] = geometry.width() / 2
            sizes.insert(frame.splitter_index + 1, geometry.width() / 2)
        else:
            sizes = [splitter.widget(i).geometry().width() for i in range(splitter.count())]
            sizes[frame.splitter_index] = geometry.height() / 2
            sizes.insert(frame.splitter_index + 1, geometry.height() / 2)

        insert_index = frame.splitter_index + 1     # get the index where the new frame should be inserted into the splitter
        new_frame = self._add_modular_frame_()  # create the new frame
        new_frame.splitter = splitter   # set the splitter of the new frame
        splitter.insertWidget(insert_index, new_frame)  # insert the new frame into the splitter
        splitter.setSizes(sizes)    # setup the proper dimensions of all the widgets in the splitter

    def _get_data_recursive_(self, widget):
        """
        Extracts dictionary that represents the hierarchical structure of the given widget (frame or splitter)
        :param widget: frame or splitter
        :return: dictionary
        """
        geometry = widget.geometry()    # get geometry for storing the proper dimensions in the dictionary
        if type(widget) == ModularFrame:
            return {'type': 'frame', 'name': widget.name, 'width': geometry.width(), 'height': geometry.height()}
        elif type(widget) == QSplitter:
            data = {'type': 'splitter', 'orientation': widget.orientation(), 'width': geometry.width(), 'height': geometry.height(), 'widgets': list()}
            for i in range(widget.count()):     # iterate through all the child widgets attached to the splitter
                child = widget.widget(i)
                data['widgets'].append(self._get_data_recursive_(child))
            return data

    def _restore_frames_recursive_(self, data, parent):
        """
        Generates widgets based on a given dictionary and attaches them to the given parent.
        :param data: dictionary with frame hierarchy data
        :param parent: parent widget (either the host itself or a splitter)
        """
        if data['type'] == 'frame':     # if the data stores a frame just add a frame
            frame = self._add_modular_frame_()
            frame.name = data['name']
            parent.addWidget(frame)
            frame.splitter = parent
        elif data['type'] == 'splitter':    # if the data stores a splitter set the splitter up
            splitter = QSplitter(data['orientation'])   # create the splitter with the proper orientation
            sizes = list()  # create a list which will hold the proper sizes for restoring the splitter properly
            for child_data in data['widgets']:  # recursively restore all child widgets of the splitter
                self._restore_frames_recursive_(child_data, splitter)
                sizes.append(child_data['width'] if data['orientation'] == Qt.Horizontal else child_data['height'])
            splitter.setSizes(sizes)    # restore the size of the splitter
            parent.addWidget(splitter)  # add the splitter to its parent

            if type(parent) != QSplitter:   # check if the newly created splitter represents the base element of the host
                self._base_splitter = splitter
                self.addWidget(splitter)

    def _setup_frame_host_(self):
        """
        Setup the first splitter containing the first frame.
        """
        self._modular_frames = list()   # create list to hold the frames

        # set initial modular frame
        self._base_splitter = QSplitter(Qt.Horizontal)  # create the first splitter (orientation really doesn't matter)
        frame = self._add_modular_frame_()      # add the first frame
        frame.splitter = self._base_splitter    # reference the splitter from within the frame
        self._base_splitter.addWidget(frame)    # add the frame to the splitter
        self.addWidget(self._base_splitter)     # add the splitter to the host

    def _on_split_horizontal_(self, frame):
        """
        Callback if a frame requests to be split horizontally.
        :param frame: the calling frame
        """
        self.split_frame(frame, Qt.Horizontal)

    def _on_split_vertical_(self, frame):
        """
        Callback if a frame requests to be split vertically.
        :param frame: the calling frame
        """
        self.split_frame(frame, Qt.Vertical)

    def _on_remove_(self, frame):
        """
        Callback if a frame requests to be removed. Does nothing if only one frame is present.
        If no frames would be left the frame host becomes unusable.
        :param frame: the calling frame
        """

        if len(self._modular_frames) > 1:   # only allow this action if there are more than one frame present
            # check if after the frame removal only one widget will be left in the splitter
            # If true, remove the splitter and reattach the remaining widget in the parent splitter (prohibit nearly empty splitters from filling up the hierarchy)

            # disconnect signals
            frame.on_split_horizontal.disconnect(self._on_split_horizontal_)
            frame.on_split_vertical.disconnect(self._on_split_vertical_)
            frame.on_remove.disconnect(self._on_remove_)
            frame.received_data_context.disconnect(self._on_data_context_received_)
            frame.data_context_removed.disconnect(self._on_data_context_removed_)

            if frame.splitter is not None and frame.splitter.count() == 2:
                last_widget = frame.splitter.widget(0) if frame.splitter.widget(1) == frame else frame.splitter.widget(1)    # find last remaining widget
                parent = frame.splitter.parent()    # find the parent splitter

                if type(parent) == QSplitter:   # if the parent is a splitter re-attach the last widget to it at the proper position where the old splitter was sitting
                    index = 0
                    for i in range(parent.count()):     # find the proper index
                        if parent.widget(i) == frame.splitter:
                            index = i
                            break
                    parent.insertWidget(index, last_widget)     # insert the last widget at the proper index
                    if type(last_widget) == ModularFrame:   # if the last widget was a frame store the splitter reference in it
                        last_widget.splitter = parent
                    frame.splitter.deleteLater()    # delete the old splitter which is now empty

            # alert that the data context of the tool frame won't be needed any longer
            if frame.loaded_tool_frame is not None and getattr(frame.loaded_tool_frame, 'data_context', False):
                self._on_data_context_removed_(frame.loaded_tool_frame.data_context)

            frame.deleteLater()     # remove the frame
            self._modular_frames.remove(frame)  # remove the frame from the list of frames

    def _on_data_context_received_(self, data_context):
        self.data_context_received.emit(data_context)

    def _on_data_context_removed_(self, data_context):
        self.data_context_removed.emit(data_context)

    def _add_modular_frame_(self):
        """
        Add a new frame.
        :return: New frame that has been setup to work with the proper event handling.
        """
        frame = ModularFrame(self, frame_search_path=self.frame_search_path)  # new frame
        frame.setFrameShape(QFrame.StyledPanel)     # add borders
        frame.on_split_horizontal.connect(self._on_split_horizontal_)    # listen for horizontal split requests
        frame.on_split_vertical.connect(self._on_split_vertical_)    # listen for vertical split requests
        frame.on_remove.connect(self._on_remove_)    # listen for removal requests
        frame.received_data_context.connect(self._on_data_context_received_)
        frame.data_context_removed.connect(self._on_data_context_removed_)
        self._modular_frames.append(frame)  # append the frame to the list of frames
        return frame    # return the newly created frame

