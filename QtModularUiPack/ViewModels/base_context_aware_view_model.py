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

from QtModularUiPack.ViewModels import BaseViewModel
from QtModularUiPack.Framework import ObservableList, is_non_strict_type, Signal


class BaseContextAwareViewModel(BaseViewModel):
    """
    Context aware view models have the ability that they can access other view models which are present in the application.
    This enables the context aware view model to control other view models.

    Important: This only works if the control is embedded in the lab master main window which handles the dependency injection!
    """

    @property
    def other_data_contexts(self):
        """
        Gets all the available data contexts
        """
        return self._other_data_contexts

    @other_data_contexts.setter
    def other_data_contexts(self, value: ObservableList):
        """
        Sets the data contexts of other view models. Makes view models available
        """
        if type(self._other_data_contexts) == ObservableList:   # check if old data context list is observable
            # de-register change events
            self._other_data_contexts.item_added.disconnect(self._other_data_context_added_)
            self._other_data_contexts.item_removed.disconnect(self._other_data_context_removed_)

        if type(value) == ObservableList:   # check if new data context list is observable
            # register change events
            self._other_data_contexts = value
            self._other_data_contexts.item_added.connect(self._other_data_context_added_)
            self._other_data_contexts.item_removed.connect(self._other_data_context_removed_)

            # add existing data contexts
            for data_context in self._other_data_contexts:
                self._other_data_context_added_(data_context)

    def __init__(self):
        super().__init__()
        self.other_data_context_was_added = Signal(BaseViewModel)
        self.other_data_context_was_removed = Signal(BaseViewModel)
        self.data_context_container = DataContexts()
        self._other_data_contexts = None
        self.other_data_contexts = ObservableList()

    def _count_instances_(self, data_context):
        """
        Counts how many view models of this type are present
        :param data_context: view model
        :return: view model count
        """
        count = 0
        for dc in self._other_data_contexts:
            if is_non_strict_type(type(dc), type(data_context)):
                count += 1
        return count

    def _other_data_context_added_(self, data_context):
        """
        Callback for handling newly added view model
        :param data_context: newly added view model
        """
        count = self._count_instances_(data_context)
        data_context_name = str(data_context).replace(' ', '')

        if hasattr(data_context, 'name'):
            data_context_name = getattr(data_context, 'name').replace(' ', '')

        if count > 1:
            data_context_name += str(count)
        self.data_context_container.__dict__[data_context_name] = data_context
        self.other_data_context_was_added.emit(data_context)

    def _other_data_context_removed_(self, data_context):
        """
        Callback for handling the removal of a view model
        :param data_context: view model that has been removed
        """
        remove_key = None
        for key in self.data_context_container.__dict__:
            if self.data_context_container.__dict__[key] == data_context:
                remove_key = key
                break
        if remove_key is not None:
            del self.data_context_container.__dict__[remove_key]
            self.other_data_context_was_removed.emit(data_context)


class DataContexts(object):
    """
    Data context container object for holding the data contexts
    """

    def help(self):
        print('\nTools Command Line help:')
        print('   Methods in tools:')
        for method in dir(self):
            if method[0:2] != '__' and method not in self.__dict__:
                print('      {}(...)'.format(method))

        print('\n   Members of tools:')
        for member in self.__dict__:
            print('      {}'.format(member))
        print('\n')

    def __init__(self):
        pass
