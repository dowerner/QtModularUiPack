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

from QtModularUiPack.Framework import Signal
from QtModularUiPack.ViewModels import BaseViewModel


class BindingEnabledWidget(object):
    """
    This class is not a visual widget but enables a widget that inherits it along with a Qt widget to do data binding.
    """

    @property
    def data_context(self):
        """
        Gets the data context of this frame
        """
        return self._data_context

    @data_context.setter
    def data_context(self, value):
        """
        Sets the data context of this frame
        """
        # alert that the old data context will be removed
        self.data_context_removed.emit(self._data_context)

        self._data_context = value
        self.bindings.destroy()     # destroy the bindings manager to remove any previous binding relationships
        self.bindings = BindingManager(self._data_context)  # create a new bindings manager

        # alert listeners that the data context of this frame was changed
        self.data_context_changed.emit(self._data_context)

    def __init__(self):
        self._data_context = None
        self.data_context_changed = Signal(BaseViewModel)
        self.data_context_removed = Signal(BaseViewModel)
        self.bindings = BindingManager(None)

    def __del__(self):
        self.bindings.destroy()


class BindingManager(object):
    """
    The bindings manager handles the bindings between widgets and the data context of a view.
    """

    def __init__(self, data_context):
        self._bindings = list()
        self._vm = data_context

    def destroy(self):
        """
        Remove all bindings and remove the listeners from the view model.
        IMPORTANT: This has to be made prior to destruction to prevent memory leaks.
        """
        for binding in self._bindings:
            binding.remove()

    def set_binding(self, variable_name, widget, widget_attribute_setter, operation=None, inv_op=None):
        """
        Set binding between a variable in the data context and a widget attribute.
        :param variable_name: name of variable in the data context to bind to
        :param widget: the widget which should be updated if the data context changes
        :param widget_attribute_setter: the attribute of the widget which should be updated
        :param operation: (Optional) an expression that process the value can be added (e.g. lambda x: not x -> inverted value gets propagated to widget)
        """
        if self._vm is None:    # do nothing if no data context is present
            return

        members = dir(self._vm)
        if variable_name in members:    # check if the variable name can be found in the data context
            existing_binding = self.get_binding(widget, widget_attribute_setter)    # check if the binding already exists
            if existing_binding is None:    # create a new binding
                self._bindings.append(Binding(variable_name, widget, widget_attribute_setter, self._vm, operation, inv_op))
            else:   # update existing binding
                existing_binding.variable_name = variable_name

    def get_binding(self, widget, widget_attribute):
        """
        Returns the binding of a given widget attribute or None if the binding does not exist
        :param widget: widget which was bound
        :param widget_attribute: attribute of the widget the data context is bound to
        :return: binding or none
        """
        if self._vm is None:
            return

        for binding in self._bindings:
            if binding.widget == widget and binding.widget_attribute_setter == widget_attribute:
                return binding
        return None


def cast_float(text):
    """
    Cast text to float (robust for conversions while line edit is being manipulated)
    :param text: Take text and try to cast it to float
    :return: number
    """
    if '.' in text:  # check for dot in string
        parts = text.split('.')
        if parts[1] == '':  # check if there is nothing written after the dot
            return 0 if parts[0] == '' else float(parts[0])     # ignore part after dot
    if text == '':
        return 0
    return float(text)  # normal conversion


def cast_int(text):
    """
    Cast text to float (permissive: also allows float conversion)
    :param text: Take text and try to cast it int (float if dot is in string)
    :return: number
    """
    if '.' in text:  # check for dot in string
        return cast_float(text)     # cast to float if non-integer was intended
    else:
        if text == '':  # return zero if string is empty
            return 0
        else:
            return int(text)    # normal conversion


class Binding(object):
    """
    A binding is used to bind a variable from a data context to the attribute of a widget.
    The binding will automatically propagate changes made in the data context to the widget and in some cases vice versa.
    """

    def _on_change_(self, name):
        """
        Callback to handle change notifications from the data context. Update widget if necessary.
        :param name: name of the changed variable
        """
        if not self._locked_during_update:
            self._locked_during_update = True
            if name == self.variable_name:  # check if this bindings variable was changed
                setter = getattr(self.widget, self.widget_attribute_setter)     # get the setter of the widget attribute
                value = getattr(self._vm, self.variable_name)   # get the value of the variable

                # if an operation was specified for this binding, apply it to the retrieved value
                if self.operation is not None:
                    value = self.operation(value)

                setter(value)   # set the widget attribute to the new value
            self._locked_during_update = False

    def _back_to_source_text_(self, text=None):
        """
        Callback to handle the propagation of widget text back to the source
        :param text: text which was changed
        """
        if not self._locked_during_update:  # check if updates are allowed
            self._locked_during_update = True   # lock binding for this operation
            if text is not None:
                if self.inv_op is not None:     # check for inverse operation to be applied to the data before being passed to the source
                    text = self.inv_op(text)    # apply inverse operation
                setattr(self._vm, self.variable_name, text)     # set data in data context source
            else:   # special case for text edit widgets
                text = self.widget.toPlainText()
                setattr(self._vm, self.variable_name, text)
            self._locked_during_update = False  # unlock binding

    def _back_to_source_check_(self, checked):
        """
        Callback to handle the propagation of data from toggle widgets back to the source
        :param checked: boolean value which was changed
        """
        if not self._locked_during_update:  # check if binding is locked
            self._locked_during_update = True   # lock binding
            if self.inv_op is not None:     # check if there is an inverse operation to be applied to the data before being passed to the source
                    checked = self.inv_op(checked)  # apply inverse operation
            setattr(self._vm, self.variable_name, checked)  # set data in data context source
            self._locked_during_update = False  # unlock binding

    def _back_to_source_index_(self, index):
        """
        Callback to handle the propagation of data from index based widgets back to the source
        :param index: index that was changed
        """
        if not self._locked_during_update:  # check if the binding is locked
            self._locked_during_update = True   # lock the binding
            if self.inv_op is not None:     # check if there is an inverse operation to be applied before passing the data to the source
                    index = self.inv_op(index)  # apply the inverse operation
            setattr(self._vm, self.variable_name, index)    # set the data in the source
            self._locked_during_update = False  # unlock the binding

    def _back_to_source_value_(self, value):
        """
        Callback to handle the propagation of numbers from widgets back to the source
        :param value: number
        """
        if not self._locked_during_update:  # check if the binding is locked
            self._locked_during_update = True   # lock the binding
            if self.inv_op is not None:     # check if there is an inverse operation to be applied before passing the data to the source
                value = self.inv_op(value)  # apply the inverse operation
            setattr(self._vm, self.variable_name, value)    # set the data in the source
            self._locked_during_update = False  # unlock the binding

    def _back_to_checked_value_(self, value):
        """
        Callback to handle the propagation of data from checkbox widgets back to the source
        :param value: boolean value
        :return:
        """
        if not self._locked_during_update:  # check if the binding is locked
            self._locked_during_update = True   # lock the binding
            if self.inv_op is not None:     # check if there is an inverse operation to be applied to the data before passing it to the source
                value = self.inv_op(value)  # apply the inverse operation
            setattr(self._vm, self.variable_name, value)    # set the data in the source
            self._locked_during_update = False  # unlock the binding

    def _register_widget_event_(self, widget, widget_attribute_setter):
        """
        Register widget events that should be propagated to data context to change variables.
        :param widget: widget to check for special signals
        :param widget_attribute_setter: attribute setter method to filter
        """
        if widget_attribute_setter == 'setText':
            self._signal = getattr(widget, 'textChanged', None)
            if self._signal is not None:
                self._signal.connect(self._back_to_source_text_)
        if widget_attribute_setter == 'setChecked':
            self._signal = getattr(widget, 'stateChanged', None)
            if self._signal is not None:
                self._signal.connect(self._back_to_source_check_)
        if widget_attribute_setter == 'setCurrentIndex':
            self._signal = getattr(widget, 'currentIndexChanged')
            if self._signal is not None:
                self._signal.connect(self._back_to_source_index_)
        if widget_attribute_setter == 'setValue':
            self._signal = getattr(widget, 'valueChanged')
            if self._signal is not None:
                self._signal.connect(self._back_to_source_value_)
        if widget_attribute_setter == 'setStart':
            self._signal = getattr(widget, 'startValueChanged')
            if self._signal is not None:
                self._signal.connect(self._back_to_source_value_)
        if widget_attribute_setter == 'setEnd':
            self._signal = getattr(widget, 'endValueChanged')
            if self._signal is not None:
                self._signal.connect(self._back_to_source_value_)
        if widget_attribute_setter == 'setChecked' and self._signal is None:
            self._signal = getattr(widget, 'toggled')
            if self._signal is not None:
                self._signal.connect(self._back_to_checked_value_)

    def remove(self):
        """
        Removes listener from data context.
        IMPORTANT: Has to be called prior to binding removal.
        """
        self._vm.property_changed.disconnect(self._on_change_)

    def _setup_source_target_type_casting_(self):
        """
        Try to implement automatic type casting such that strings and numbers can be converted in bindings
        """
        value = getattr(self._vm, self.variable_name)
        if value is not None:
            if (type(value) == int or type(value) == float) and self.widget_attribute_setter == 'setText':
                cast = cast_int if type(value) == int else cast_float

                if self.inv_op is not None:
                    self.inv_op = lambda v: self.inv_op(cast(v))
                else:
                    self.inv_op = cast

                if self.operation is not None:
                    self.operation = lambda v: str(self.operation(v))
                else:
                    self.operation = lambda v: str(v)

    def __init__(self, variable_name, widget, widget_attribute_setter, data_context, operation=None, inv_op=None):
        self._locked_during_update = False
        self.operation = operation
        self.inv_op = inv_op
        self._vm = data_context
        self._vm.property_changed.connect(self._on_change_)     # listen to changes in the source
        self.variable_name = variable_name      # name to listen for in changes
        self.widget = widget    # widget to apply the changes to
        self.widget_attribute_setter = widget_attribute_setter  # setter method in widget
        self._signal = None     # signal to listen for in widget to apply changes to the source (reverse-direction)
        self._register_widget_event_(widget, widget_attribute_setter)   # check widget for valid signals
        self._setup_source_target_type_casting_()   # use operation/inv_op to setup type-casting (This enables the usage of number based data in e.g. QLineEdit widgets)
        self._on_change_(self.variable_name)    # apply the current data to the widget
