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