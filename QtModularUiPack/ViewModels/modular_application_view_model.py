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

from QtModularUiPack.ViewModels import BaseViewModel, BaseContextAwareViewModel
from QtModularUiPack.Framework import ObservableList


class ModularApplicationViewModel(BaseViewModel):
    """
    This view model is used as data-context for the modular application
    """

    def __init__(self):
        super().__init__()
        self.context_aware_view_models = ObservableList()
        self.other_data_contexts = ObservableList()  # filled via dependency injection

    def connect_context_aware_view_model(self, context_aware_vm: BaseContextAwareViewModel):
        """
        Provide the context aware view model with all other available view models
        :param context_aware_vm: context aware view model
        """
        self.context_aware_view_models.append(context_aware_vm)
        context_aware_vm.other_data_contexts = self.other_data_contexts

    def disconnect_context_aware_view_model(self, context_aware_vm: BaseContextAwareViewModel):
        """
        Remove the context aware view model from the event system
        :param context_aware_vm: context aware view model to be removed
        """
        context_aware_vm.other_data_contexts = None
        if context_aware_vm in self.context_aware_view_models:
            self.context_aware_view_models.remove(context_aware_vm)

    def save_configuration(self):
        for vm in self.other_data_contexts:
            if 'save_configuration' in dir(vm):
                vm.save_configuration()
