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

from QtModularUiPack.Framework.Extensions import Signal


class ObservableList(list):
    """
    This list can send notifications about changes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_added = Signal(object)
        self.item_removed = Signal(object)
        self.on_clear = Signal()

    def append(self, item):
        """
        Append item to the list. (Will also trigger notification)
        :param item: item to append to the list
        """
        super().append(item)
        self.item_added.emit(item)

    def remove(self, item):
        """
        Remove item from the list. (Will also trigger notification)
        :param item: item to remove from the list
        """
        super().remove(item)
        self.item_removed.emit(item)

    def clear(self):
        """
        Remove all items from list.
        """
        super().clear()
        self.on_clear.emit()
