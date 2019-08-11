import numpy as np


OP_ADD = '+'
OP_SUB = '-'
OP_MUL = '*'
OP_DIV = '/'


class CalculatorModel(object):

    def __init__(self):
        self.operands = [0]
        self.operations = list()

    def clear(self):
        self.operands = [0]
        self.operations = list()

    def add_operation(self, operand, operation):
        self.operands.append(operand)
        self.operations.append(operation)

    def add(self, number):
        self.add_operation(OP_ADD, number)

    def sub(self, number):
        self.add_operation(OP_SUB, number)

    def mul(self, number):
        self.add_operation(OP_MUL, number)

    def div(self, number):
        self.add_operation(OP_DIV, number)

    def evaluate(self):
        result = self.operands[0]
        for i in range(len(self.operations)):
            if self.operations[i] == OP_ADD:
                result += self.operands[i + 1]
            if self.operations[i] == OP_DIV:
                result -= self.operands[i + 1]
            if self.operations[i] == OP_MUL:
                result *= self.operands[i + 1]
            if self.operations[i] == OP_DIV:
                result /= self.operands[i + 1]
        self.clear()
        self.operands[0] = result
        return result

