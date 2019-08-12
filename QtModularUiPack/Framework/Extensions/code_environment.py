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

import traceback


class CodeEnvironment(object):
    """
    The code environment allows the execution of code and stores all local variables in a separate context
    """

    @property
    def local_variables(self):
        """
        Gets the local variables which are available in the execution context of the environment.
        """
        return self._local_variables

    def __init__(self):
        self._local_variables = dict()

    def run(self, code, raise_exceptions=False):
        """
        Run python code
        :param code: code to run
        :param raise_exceptions: if set to true the environment will let the caller handle exceptions
        """
        try:
            # load local variables
            local_variables = locals()

            for local in self._local_variables:
                if local != 'self' and local != 'tools' and local != 'local_variables':
                    local_variables[local] = self._local_variables[local]

            # run code
            exec(code)

            # store created variables global
            for local in list(local_variables.keys()):
                if local != 'self' and local != 'tools' and local != 'local_variables':
                    self._local_variables[local] = local_variables[local]
        except Exception as e:
            traceback.print_exc()
            print('Error during command execution, Error: {}'.format(e))
            if raise_exceptions:
                raise e
