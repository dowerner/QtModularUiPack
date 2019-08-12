from QtModularUiPack.Widgets import EmptyFrame
from calculator_view_model import CalculatorViewModel
from calculator_model import OP_ADD, OP_SUB, OP_MUL, OP_DIV
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt


class CalculatorView(EmptyFrame):
    """
    This is the view of the calculator: By inheriting EmptyFrame this widget can be used as a standalone application
    or as a widget inside a modular application. It is also compatible to be used in any other PyQt application.

    Binding: EmptyFrame can use child classes which inherit from BaseViewModel or BaseContextAwareViewModel as data-context
        PyQt widgets (QLabel, QPushButton, QCheckBox, ...) have setter methods like "setText", "setValue", etc.
        Classes derived from EmptyFrame can bind variable name from the data-context to those setter methods e.g.:

            help_box = QLabel()
            helpful_check = QCheckBox('This was helpful')
            self.binding.set_binding('help_text', help_box, 'setText')
            self.binding.set_binding('was_helpful', helpful_check, 'setChecked')

        This would create two widgets (help_box, helpful_check) and bind them to the variables "help_text" and "was_helpful".
        The binding manager makes sure that proper data-type conversion is made.

        The bindings are bidirectional meaning that for instance checking the checkbox on the UI which is bound to
        a variable in the data-context will change the variable in the data-context.
    """

    name = 'simple calculator'      # by overwriting this constant we change the standalone application default title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # initialize EmptyFrame
        self.data_context = CalculatorViewModel()   # add view model as data context to which this widget binds

        main_layout = QGridLayout()     # create grid layout for display and calculator buttons
        self.setLayout(main_layout)

        display = QLabel()  # use QLabel as display
        self.bindings.set_binding('display_content', display, 'setText')    # bind variable "display_content" to QLabel
        main_layout.addWidget(display, 0, 0, 1, 4, Qt.AlignCenter)

        # add the buttons for the digits
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

        # add the buttons for the operations
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

