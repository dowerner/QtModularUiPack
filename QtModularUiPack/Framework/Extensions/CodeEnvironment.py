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


if __name__ == '__main__':
    ce = CodeEnvironment()
    ce.run('import matplotlib.pyplot as plt')
    ce.run('import numpy as np')
    ce.run('def test(a, b):\n\treturn a + b')
    ce.run('x = np.linspace(0, 6*np.pi, 1000)')
    ce.run('y = test(np.cos(x), 10)')
    ce.run('plt.figure()\nplt.plot(x, y)\nplt.show()')
