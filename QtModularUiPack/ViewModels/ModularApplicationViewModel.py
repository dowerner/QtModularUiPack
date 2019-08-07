from ViewModels import BaseViewModel, BaseContextAwareViewModel
from Framework import ObservableList


class ModularApplicationViewModel(BaseViewModel):

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
