def is_non_strict_type(type1, compare_type):
    """
    Returns true if the given type is the same as a comparison type but does it less rigorous than issubclass().
    The main advantage is that classes of modules which where reloaded during runtime are still recognized.
    WARNING: If the name of a class in a different module is the same as in the module in question, this method will
    still return true.
    :param type1: type in question
    :param compare_type: type to compare the type in question to
    :return: True or False
    """
    if isinstance(type1, type) and type1.__name__ == compare_type.__name__:
        return True
    else:
        return False


def is_non_strict_subclass(subtype, parent_type):
    """
    Returns true if the given type inherits the subtype but does it less rigorous than issubclass().
    The main advantage is that classes of modules which where reloaded during runtime are still recognized as sub classes
    of previously loaded module classes.
    WARNING: If the name of a class in a different module is the same as in the module in question, this method will
    still return true.
    :param subtype: Type that is derived
    :param parent_type: Parent that was inherited
    :return: True or False
    """
    if is_non_strict_type(subtype, parent_type):
        return True

    if hasattr(subtype, '__bases__'):
        base_classes = list(subtype.__bases__)
        for base_class in base_classes:
            if base_class.__name__ == parent_type.__name__:
                return True
    return False