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

from QtModularUiPack.Framework.Extensions import Singleton
from QtModularUiPack.Framework.ImportTools.utils import is_non_strict_subclass, is_non_strict_type
import importlib
import os
import sys


@Singleton
class ModuleManager(object):
    """
    Handles the loading and reloading of python modules.
    """

    def __init__(self):
        self._dirty = dict()
        self.loaded_classes = dict()

    def reload_modules(self):
        """
        Reloads all modules that were previously loaded by using the manager.
        IMPORTANT: Does not reload all modules.
        """
        modules_to_reload = list()      # store modules to reload
        for path in self.loaded_classes:    # iterate through all loaded classes

            # mark given class path as dirty
            # -> this means that the classes were reloaded but that if the load_classes_from_folder_derived_from() method
            #    is called again it should not just return the known types but also look for new ones.
            self._dirty[path] = True

            for cls in self.loaded_classes[path]:
                class_module = sys.modules[cls.__module__]  # get the module of the class

                # check for modules that are being used by this module to reload them as well
                for member_key in class_module.__dict__:
                    member = class_module.__dict__[member_key]
                    if isinstance(member, type):    # check if the member is a class
                        if member.__module__ not in modules_to_reload:  # check if the members module is already scheduled to be reloaded
                            modules_to_reload.append(member.__module__)

                if cls.__module__ not in modules_to_reload:     # schedule class module to be reloaded if not done already
                    modules_to_reload.append(cls.__module__)

        # reload all modules that have dependencies on the classes
        for module_path in modules_to_reload:
            sys.modules[module_path] = importlib.reload(sys.modules[module_path])

    def load_classes_from_folder_derived_from(self, path, parent_class):
        """
        Tries to load all classes that are discovered in a folder which inherit from a given parent type.
        :param path: Path to look for classes
        :param parent_class: class that should be inherited
        :return: list of classes
        """

        """
        Explanation of dirty: If a path is marked dirty this means that the classes have been reloaded properly but that
        it has not yet been checked if any new classes were added to said path. Therefore, the present classes should be
        returned and at the same time new once should be searched.
        """

        if path in self.loaded_classes and not self._dirty[path]:
            return self.loaded_classes[path]     # return already loaded types if they are not marked dirty

        types_loaded = list()

        for file in os.listdir(path):
            if file[-3:].lower() == '.py':  # check if file is a python script
                module_name, module_ext = os.path.splitext(file)

                if path not in sys.path:
                    sys.path.append(path)   # append the module path to the environment

                if module_name not in sys.modules:  # only do this if the module wasn't already reloaded before and is present (otherwise the classes cannot be extracted properly)
                    module = __import__(module_name)    # import the module
                    sys.modules[module_name] = module
                else:
                    module = sys.modules[module_name]

                mod_dict = module.__dict__
                for name in mod_dict:   # search for valid classes
                    cls = mod_dict[name]
                    if isinstance(cls, type) and is_non_strict_subclass(mod_dict[name], parent_class):    # check if sub class of EmptyFrame
                        # add the class to the list of loaded types but only if it is not already present
                        # -> this is necessary since the imports in different modules will produce duplicates
                        already_present = False
                        for added_class in types_loaded:
                            if is_non_strict_type(cls, added_class):
                                already_present = True
                                break
                        if not already_present:
                            types_loaded.append(cls)

        self.loaded_classes[path] = types_loaded
        self._dirty[path] = False
        return types_loaded

