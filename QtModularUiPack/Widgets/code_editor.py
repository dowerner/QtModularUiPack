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

from PyQt5.QtGui import QSyntaxHighlighter, QTextDocument, QTextCharFormat, QFont, QTextCursor
from PyQt5.QtCore import Qt, QRegularExpression, pyqtSignal
from PyQt5.QtWidgets import QTextEdit


class HighlightingRule(object):
    """
    Rule for highlighting text
    """

    def __int__(self):
        self.pattern = None
        self.format = None


def index_in_str(text, substring, starting=0):
    """
    Gets index of text in string
    :arg text: text to search through
    :arg substring: text to search for
    :arg starting: offset
    :return position
    """

    search_in = text[starting:]
    if substring in search_in:
        return search_in.index(substring)
    else:
        return -1


class SyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for python
    """

    def __init__(self, parent: QTextDocument = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # private members
        self._comment_start_expression = None
        self._comment_end_expression = None
        self._keyword_format = QTextCharFormat()
        self._class_format = QTextCharFormat()
        self._single_line_comment_format = QTextCharFormat()
        self._multi_line_comment_format = QTextCharFormat()
        self._quotation_format = QTextCharFormat()
        self._function_format = QTextCharFormat()
        self._highlighting_rules = list()

        # highlighting rules
        self._keyword_format.setForeground(Qt.darkBlue)
        self._keyword_format.setFontWeight(QFont.Bold)

        keywords = ['class', 'def', 'return' 'self', 'float', 'int', 'list', 'dict', 'if', 'else', 'elif', 'pass', 'None', 'object', 'for', 'while', 'is', 'in', 'print', 'round', 'min', 'max', 'abs', 'lambda', 'import', 'as', 'from', 'and', 'or']
        keyword_patterns = ['\\b{}\\b'.format(keyword) for keyword in keywords]

        for pattern in keyword_patterns:
            rule = HighlightingRule()
            rule.pattern = QRegularExpression(pattern)
            rule.format = self._keyword_format
            self._highlighting_rules.append(rule)

        self._class_format.setFontWeight(QFont.Bold)
        self._class_format.setForeground(Qt.darkMagenta)
        rule = HighlightingRule()
        rule.pattern = QRegularExpression('\\bQ[A-Za-z+\\b]')
        rule.format = self._class_format
        self._highlighting_rules.append(rule)

        self._quotation_format.setFontWeight(QFont.Bold)
        self._quotation_format.setForeground(Qt.darkGreen)
        rule = HighlightingRule()
        rule.pattern = QRegularExpression('".*"')
        rule.format = self._quotation_format
        self._highlighting_rules.append(rule)
        rule = HighlightingRule()
        rule.pattern = QRegularExpression("'.*'")
        rule.format = self._quotation_format
        self._highlighting_rules.append(rule)

        self._function_format.setForeground(Qt.blue)
        rule = HighlightingRule()
        rule.pattern = QRegularExpression('\\b[A-Za-z0-9_]+(?=\\())')
        rule.format = self._function_format
        self._highlighting_rules.append(rule)

        self._single_line_comment_format.setForeground(Qt.gray)
        rule = HighlightingRule()
        rule.pattern = QRegularExpression('#[^\n]*')
        rule.format = self._single_line_comment_format
        self._highlighting_rules.append(rule)

        self._multi_line_comment_format.setForeground(Qt.gray)
        self._comment_start_expression = QRegularExpression('"""*')
        self._comment_end_expression = QRegularExpression('*"""')

    def highlightBlock(self, p_str):
        for rule in self._highlighting_rules:
            match_iterator = rule.pattern.globalMatch(p_str)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), rule.format)
        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            start_index = index_in_str(p_str, self._comment_start_expression.pattern())

        while start_index >= 0:
            match = self._comment_end_expression.match(p_str, start_index)
            end_index = match.capturedStart()
            comment_length = 0
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(p_str) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()
            self.setFormat(start_index, comment_length, self._multi_line_comment_format)
            start_index = index_in_str(p_str, self._comment_start_expression.pattern(), start_index + comment_length)


class CodeEditor(QTextEdit):
    """
    Code editor widget for python
    """
    textChanged = pyqtSignal(str)

    @property
    def font_size(self):
        """
        Gets font size
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        """
        Sets font size
        :param value: size
        """
        self._font_size = value
        self._update_()

    @property
    def tab_stop_width(self):
        """
        Gets tab width
        """
        return self._tab_stop_width

    @tab_stop_width.setter
    def tab_stop_width(self, value):
        """
        Sets tab width
        :param value: width
        """
        self._tab_stop_width = value
        self._update_()

    @property
    def text(self):
        """
        Gets text
        """
        return self.toPlainText()

    @text.setter
    def text(self, value):
        """
        Sets text
        :param value: code
        """
        self.setPlainText(value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._highlighter = SyntaxHighlighter(self)
        self._font_size = 10
        self._tab_stop_width = 4
        self._last_button = None
        self._lock_auto_indentation_ = False
        self._setup_()

    def setText(self, text):
        self.setPlainText(text)

    def _update_(self):
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(self._font_size)

        self.setFont(font)
        self.setTabStopWidth(self._tab_stop_width * self.fontMetrics().width(' '))

    def keyPressEvent(self, event):
        # Shift + Tab is not the same as trying to catch a Shift modifier and a tab Key.
        # Shift + Tab is a Backtab!!
        if event.key() == Qt.Key_Backtab:
            cur = self.textCursor()
            # Copy the current selection
            pos = cur.position() # Where a selection ends
            anchor = cur.anchor() # Where a selection starts (can be the same as above)

            # Can put QtGui.QTextCursor.MoveAnchor as the 2nd arg, but this is the default
            cur.setPosition(pos)

            # Move the position back one, selection the character prior to the original position
            cur.setPosition(pos-1, QTextCursor.KeepAnchor)

            if str(cur.selectedText()) == "\t":
                # The prior character is a tab, so delete the selection
                cur.removeSelectedText()
                # Reposition the cursor with the one character offset
                cur.setPosition(anchor-1)
                cur.setPosition(pos-1, QTextCursor.KeepAnchor)
            else:
                # Try all of the above, looking before the anchor (This helps if the achor is before a tab)
                cur.setPosition(anchor)
                cur.setPosition(anchor-1, QTextCursor.KeepAnchor)
                if str(cur.selectedText()) == "\t":
                    cur.removeSelectedText()
                    cur.setPosition(anchor-1)
                    cur.setPosition(pos-1, QTextCursor.KeepAnchor)
                else:

                    # Its not a tab, so reset the selection to what it was
                    cur.setPosition(anchor)
                    cur.setPosition(pos, QTextCursor.KeepAnchor)
        elif event.key() == Qt.Key_Return:
            super().keyPressEvent(event)
            text = self.toPlainText()
            lines = text.split('\n')
            current_line = self.textCursor().blockNumber()

            if current_line > 0:
                last_line = lines[current_line - 1]

                if len(last_line) > 0:
                    old_indent = ''
                    chr_ = last_line[0]
                    i = 0
                    while chr_ == ' ' or chr_ == '\t':
                        old_indent += chr_
                        i += 1
                        if i == len(last_line):
                            break
                        chr_ = last_line[i]

                    self.insertPlainText(old_indent)
                    if last_line[-1] == ':':
                        self.insertPlainText('\t')
        else:
            return super().keyPressEvent(event)

    def _text_changed_(self):
        self.textChanged.emit(self.toPlainText())

    def _setup_(self):
        self.setLineWrapMode(QTextEdit.NoWrap)
        self._update_()
        self._highlighter = SyntaxHighlighter(self.document())
        super().textChanged.connect(self._text_changed_)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.Qt import QApplication

    class MainWindow(QMainWindow):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._editor = CodeEditor()
            self._editor.textChanged.connect(self.callback)
            self.setCentralWidget(self._editor)
            self.setWindowTitle('Code Editor Test')

        def callback(self, text):
            print(text)


    app = QApplication([])
    main = MainWindow()
    main.show()
    QApplication.instance().exec_()
