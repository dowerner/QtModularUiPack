from Framework.Extensions import Signal


class ObservableList(list):
    """
    This list can send notifications about changes.
    """
    item_added = Signal(object)
    item_removed = Signal(object)
    on_clear = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
