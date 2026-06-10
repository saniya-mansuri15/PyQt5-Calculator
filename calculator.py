"""
PyQt5 Calculator - College Assignment
A GUI calculator built with PyQt5 featuring dark theme, input validation,
error handling, keyboard support, and theme toggle.
"""

import re
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QPushButton,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent


# Operators shown on buttons and used in expressions
OPERATORS = {"+", "-", "×", "÷", "%"}


class Calculator(QWidget):
    """Main calculator window with display, button grid, and theme support."""

    def __init__(self):
        super().__init__()
        self.dark_mode = True
        self.just_calculated = False
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        """Build the window layout: display, theme toggle, and button grid."""
        self.setWindowTitle("PyQt5 Calculator")
        self.setFixedSize(360, 500)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Top row: display and dark/light mode toggle
        top_row = QHBoxLayout()

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setPlaceholderText("0")
        top_row.addWidget(self.display)

        self.theme_button = QPushButton("☀")
        self.theme_button.setFixedSize(44, 44)
        self.theme_button.setToolTip("Toggle dark / light mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        top_row.addWidget(self.theme_button)

        main_layout.addLayout(top_row)

        # 5 x 4 button grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)

        button_labels = [
            ["C", "AC", "Del", "%"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]

        for row_index, row_labels in enumerate(button_labels):
            for col_index, label in enumerate(row_labels):
                button = QPushButton(label)
                button.setMinimumHeight(52)
                button.clicked.connect(
                    lambda checked, text=label: self.on_button_click(text)
                )
                grid_layout.addWidget(button, row_index, col_index)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

        # Allow keyboard input when window is focused
        self.setFocusPolicy(Qt.StrongFocus)

    def toggle_theme(self):
        """Switch between dark and light colour themes."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        """Apply stylesheet colours for the current theme."""
        if self.dark_mode:
            self.theme_button.setText("☀")
            base_style = """
                QWidget {
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                    font-family: Segoe UI, Arial, sans-serif;
                }
                QLineEdit {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: 2px solid #45475a;
                    border-radius: 8px;
                    font-size: 26px;
                    padding: 12px;
                }
                QPushButton {
                    background-color: #45475a;
                    color: #cdd6f4;
                    border: none;
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #585b70; }
                QPushButton:pressed { background-color: #6c7086; }
            """
            operator_style = "QPushButton { background-color: #89b4fa; color: #1e1e2e; }"
            equals_style = "QPushButton { background-color: #a6e3a1; color: #1e1e2e; }"
            clear_style = "QPushButton { background-color: #f38ba8; color: #1e1e2e; }"
        else:
            self.theme_button.setText("🌙")
            base_style = """
                QWidget {
                    background-color: #f5f5f5;
                    color: #212121;
                    font-family: Segoe UI, Arial, sans-serif;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #212121;
                    border: 2px solid #bdbdbd;
                    border-radius: 8px;
                    font-size: 26px;
                    padding: 12px;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #212121;
                    border: none;
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #d5d5d5; }
                QPushButton:pressed { background-color: #bdbdbd; }
            """
            operator_style = "QPushButton { background-color: #1976d2; color: #ffffff; }"
            equals_style = "QPushButton { background-color: #388e3c; color: #ffffff; }"
            clear_style = "QPushButton { background-color: #d32f2f; color: #ffffff; }"

        self.setStyleSheet(base_style)

        # Colour-code buttons by their role
        for button in self.findChildren(QPushButton):
            if button is self.theme_button:
                continue
            label = button.text()
            if label in ("+", "-", "×", "÷", "%"):
                button.setStyleSheet(operator_style)
            elif label == "=":
                button.setStyleSheet(equals_style)
            elif label in ("C", "AC", "Del"):
                button.setStyleSheet(clear_style)
            else:
                button.setStyleSheet("")

    def on_button_click(self, text):
        """Route each button press to the correct handler."""
        if text == "AC":
            self.clear_all()
        elif text in ("C", "Del"):
            self.delete_last()
        elif text == "=":
            self.calculate_result()
        else:
            self.append_input(text)

    def clear_all(self):
        """AC - wipe the display completely."""
        self.display.clear()
        self.just_calculated = False

    def delete_last(self):
        """C / Del - remove the last typed character."""
        current_text = self.display.text()
        if current_text == "Error":
            self.display.clear()
        elif current_text:
            self.display.setText(current_text[:-1])
        self.just_calculated = False

    def get_last_number(self, expression):
        """Return the number segment after the last operator."""
        last_number = expression
        for operator in ("+", "-", "×", "÷", "%"):
            if operator in expression:
                last_number = expression.rsplit(operator, 1)[-1]
        return last_number

    def append_input(self, text):
        """Add a digit, operator, or decimal with validation rules."""
        current_text = self.display.text()

        if current_text == "Error":
            current_text = ""

        # After a result, start a new number unless user continues with an operator
        if self.just_calculated:
            if text in OPERATORS:
                self.just_calculated = False
            elif text.isdigit() or text == ".":
                current_text = ""
                self.just_calculated = False

        # Block operators at the very start (allow minus for negative numbers)
        if not current_text and text in OPERATORS and text != "-":
            return

        # Replace consecutive operators instead of stacking them
        if text in OPERATORS and current_text and current_text[-1] in OPERATORS:
            if text == "-" and current_text[-1] in "×÷+%":
                pass  # allow negative number after multiply/divide/etc.
            else:
                current_text = current_text[:-1]

        # Prevent a second decimal point in the same number
        if text == ".":
            last_number = self.get_last_number(current_text)
            if "." in last_number:
                return
            if not last_number and (not current_text or current_text[-1] in OPERATORS):
                current_text += "0"

        self.display.setText(current_text + text)

    def prepare_expression(self, expression):
        """Convert display symbols to Python syntax and handle percentages."""
        expr = expression.replace("×", "*").replace("÷", "/")
        # Turn 50% into (50/100) for percentage calculations
        expr = re.sub(r"(\d+\.?\d*)%", r"(\1/100)", expr)
        return expr

    def format_result(self, result, original_expression):
        """Format numbers cleanly; keep one decimal when inputs used decimals."""
        if isinstance(result, float):
            if "." in original_expression and result.is_integer():
                return f"{int(result)}.0"
            if result.is_integer():
                return str(int(result))
            return str(result)
        return str(result)

    def calculate_result(self):
        """Evaluate the expression safely and show the result or 'Error'."""
        expression = self.display.text().strip()

        # Reject empty input or expressions ending with an operator
        if not expression or expression[-1] in OPERATORS:
            return

        try:
            python_expr = self.prepare_expression(expression)

            # Catch obvious division-by-zero patterns
            if re.search(r"/\s*0(?!\d)", python_expr):
                self.display.setText("Error")
                self.just_calculated = False
                return

            result = eval(python_expr)
            self.display.setText(self.format_result(result, expression))
            self.just_calculated = True

        except (SyntaxError, ZeroDivisionError, TypeError, NameError, ValueError):
            self.display.setText("Error")
            self.just_calculated = False

    def keyPressEvent(self, event: QKeyEvent):
        """Keyboard shortcuts mirror the on-screen buttons."""
        key = event.key()
        text = event.text()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.calculate_result()
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_last()
        elif key == Qt.Key_Escape:
            self.clear_all()
        elif text.isdigit() or text in "+-.=%":
            if text == "*":
                self.append_input("×")
            elif text == "/":
                self.append_input("÷")
            else:
                self.append_input(text)
        else:
            super().keyPressEvent(event)


def main():
    """Launch the calculator application."""
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
