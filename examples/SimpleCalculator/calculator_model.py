OP_ADD = '+'
OP_SUB = '-'
OP_MUL = '*'
OP_DIV = '/'

PRECEDENT_OPS = [OP_MUL, OP_DIV]


class CalculatorModel(object):
    """
    This is the model of the calculator: Note that there is absolutely no care taken of any view related issues
    """

    def __init__(self):
        self.operands = [0]     # store the operands of the expression for evaluation
        self.operations = list()    # store the operations to apply to the operands

    def clear(self):
        """
        Reset the calculator to zero
        """
        self.operands = [0]
        self.operations = list()

    @staticmethod
    def apply_op(operation, number1, number2):
        """
        Apply operation on two numbers
        :param operation: text representing operation
        :param number1: first operand
        :param number2: second operand
        """
        if operation == OP_ADD:
            return number1 + number2
        elif operation == OP_SUB:
            return number1 - number2
        elif operation == OP_MUL:
            return number1 * number2
        elif operation == OP_DIV:
            return number1 / number2    # the view model will take care of handling exceptions from zero division
        return 0

    def evaluate(self):
        """
        Evaluate the expression stored in the calculator
        :return: result of the calculation
        """
        result = self.operands[0]   # get first number (result if no operations have been added)

        # get all operations which have to be evaluated first: *, /
        precedent_ops_idx = [i for i in range(len(self.operations)) if self.operations[i] in PRECEDENT_OPS]

        # evaluate terms which have priority
        shift = 0
        for i in precedent_ops_idx:
            result = self.apply_op(self.operations[i], self.operands[i + shift], self.operands[i + 1 + shift])
            self.operands[i + shift] = result
            del self.operands[i + 1 + shift]
            shift -= 1

        # remove all operations which were already used
        self.operations = [self.operations[i] for i in range(len(self.operations)) if self.operations[i] not in PRECEDENT_OPS]

        # evaluate the remaining terms
        shift = 0
        for i in range(len(self.operations)):
            result = self.apply_op(self.operations[i], self.operands[i + shift], self.operands[i + 1 + shift])
            self.operands[i + shift] = result
            del self.operands[i + 1 + shift]
            shift -= 1

        self.clear()    # clear calculator
        self.operands[0] = result   # use result as initial value
        return result


if __name__ == '__main__':
    # Test calculator
    calc = CalculatorModel()
    calc.operands = [36, 8, 2, 4, 4, 5]
    calc.operations = ['+', '/', '*', '/', '+']
    print(calc.evaluate())  # should give 45.0

