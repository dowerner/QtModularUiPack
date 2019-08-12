from QtModularUiPack.ViewModels import BaseViewModel
from calculator_model import CalculatorModel


class CalculatorViewModel(BaseViewModel):
    """
    The view model is the data-context for the view: It formats the data in order to be presented
    and communicated with the model
    """

    @property
    def display_content(self):
        """
        Gets the content to be displayed in the display of the calculator
        """
        if self._has_error:     # check error flag
            self._has_error = False     # reset error flag
            return 'ZERO DIVISION ERROR'    # get error message

        # build display string from model data
        content = (''.join(['{}'+op for op in self._calculator.operations])+'{}').format(*self._calculator.operands)
        return content

    def __init__(self):
        super().__init__()  # initialize data-context
        self._calculator = CalculatorModel()    # create instance of model
        self._has_error = False     # initialize error flag

    def enter_number(self, number):
        """
        Add digit to current number
        :param number: digit
        """
        value = self._calculator.operands[-1]    # get last number of expression in display
        self._calculator.operands[-1] = 10 * value + number     # shift last number and add new digit
        self.notify_change('display_content')   # notify view about change

    def enter_operator(self, operator):
        """
        Add operator to expression
        :param operator: +, -, *, /
        """
        self._calculator.operations.append(operator)    # append operator
        self._calculator.operands.append(0)     # append zero in order for the expression to stay valid
        self.notify_change('display_content')   # notify view about change

    def clear(self, *args):
        """
        Set expression to zero
        :param args: Argument needed to be valid Qt slot
        """
        self._calculator.clear()
        self.notify_change('display_content')   # notify view about change

    def evaluate(self, *args):
        """
        Evaluate current expression
        :param args: Argument needed to be valid Qt slot
        """
        try:
            self._calculator.evaluate()     # evaluate expression in model
        except ZeroDivisionError:   # catch zero-division errors
            self._calculator.clear()    # clear calculator
            self._has_error = True      # set error flag to true

        self.notify_change('display_content')   # notify view about change
