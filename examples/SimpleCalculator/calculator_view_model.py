from QtModularUiPack.ViewModels import BaseViewModel
from calculator_model import CalculatorModel


class CalculatorViewModel(BaseViewModel):

    @property
    def display_content(self):
        content = (''.join(['{}'+op for op in self._calculator.operations])+'{}').format(*self._calculator.operands)
        return content

    def __init__(self):
        super().__init__()

        self._calculator = CalculatorModel()

    def enter_number(self, number):
        index = len(self._calculator.operations)
        value = self._calculator.operands[index]
        self._calculator.operands[index] = 10 * value + number
        self.notify_change('display_content')

    def enter_operator(self, operator):
        self._calculator.operations.append(operator)
        self._calculator.operands.append(0)
        self.notify_change('display_content')

    def clear(self, *args):
        self._calculator.clear()
        self.notify_change('display_content')

    def evaluate(self, *args):
        self._calculator.evaluate()
        self.notify_change('display_content')
