from QtModularUiPack.Widgets import EmptyFrame
from calculator_view_model import CalculatorViewModel
from calculator_model import OP_ADD, OP_SUB, OP_MUL, OP_DIV
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt


class CalculatorView(EmptyFrame):

    name = 'simple calculator'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_context = CalculatorViewModel()

        main_layout = QGridLayout()
        self.setLayout(main_layout)

        display = QLabel()
        self.bindings.set_binding('display_content', display, 'setText')
        main_layout.addWidget(display, 0, 0, 1, 4, Qt.AlignCenter)

        num = 1
        for i in range(3):
            for j in range(3):
                num_button = QPushButton(str(num))
                num_button.clicked.connect(lambda click_arg, x=num: self.data_context.enter_number(x))
                main_layout.addWidget(num_button, i + 1, j)
                num += 1
        num_button = QPushButton('0')
        num_button.clicked.connect(lambda click_arg: self.data_context.enter_number(0))
        main_layout.addWidget(num_button, 4, 1)

        operations = [OP_ADD, OP_SUB, OP_MUL, OP_DIV]
        for i in range(len(operations)):
            op = operations[i]
            op_button = QPushButton(op)
            op_button.clicked.connect(lambda click_arg, x=op: self.data_context.enter_operator(x))
            main_layout.addWidget(op_button, i + 1, 3)
        clear_button = QPushButton('clear')
        clear_button.clicked.connect(self.data_context.clear)
        evaluate_button = QPushButton('evaluate')
        evaluate_button.clicked.connect(self.data_context.evaluate)
        main_layout.addWidget(clear_button, 5, 0, 1, 2, Qt.AlignCenter)
        main_layout.addWidget(evaluate_button, 5, 2, 1, 2, Qt.AlignCenter)




