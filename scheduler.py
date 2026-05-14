# Copyright 2023 Felipe Cupido
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from PyQt5 import QtCore, QtWidgets
import piplates.RELAYplate as RELAY
import re

class TouchSpinBox(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._minimum = 0
        self._maximum = 10000
        self._suffix = ""
        self._special_value_text = ""

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.btn_minus = QtWidgets.QPushButton("-")
        self.btn_minus.setFixedWidth(40)
        self.btn_minus.clicked.connect(self.decrement)

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setMinimumWidth(80)
        self.line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.line_edit.editingFinished.connect(self.on_editing_finished)

        self.btn_plus = QtWidgets.QPushButton("+")
        self.btn_plus.setFixedWidth(40)
        self.btn_plus.clicked.connect(self.increment)

        self.layout.addWidget(self.btn_minus)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.btn_plus)

        self.update_text()

    def setMinimum(self, val):
        self._minimum = val
        if self._value < val:
            self._value = val
        self.update_text()

    def setMaximum(self, val):
        self._maximum = val
        if self._value > val:
            self._value = val
        self.update_text()

    def setSuffix(self, suffix):
        self._suffix = suffix
        self.update_text()

    def setSpecialValueText(self, text):
        self._special_value_text = text
        self.update_text()

    def setSingleStep(self, step):
        # We don't use single step for now but we keep the method for compatibility
        pass

    def value(self):
        return self._value

    def setValue(self, val):
        if val < self._minimum: val = self._minimum
        if val > self._maximum: val = self._maximum
        self._value = val
        self.update_text()

    def update_text(self):
        if self._value == self._minimum and self._special_value_text:
            self.line_edit.setText(self._special_value_text)
        else:
            self.line_edit.setText(str(self._value) + self._suffix)

    def increment(self):
        if self._value < self._maximum:
            self._value += 1
            self.update_text()

    def decrement(self):
        if self._value > self._minimum:
            self._value -= 1
            self.update_text()

    def on_editing_finished(self):
        text = self.line_edit.text()
        if self._suffix and text.endswith(self._suffix):
            text = text[:-len(self._suffix)]

        if self._special_value_text and text == self._special_value_text:
            self._value = self._minimum
        else:
            try:
                match = re.search(r'-?\d+', text)
                if match:
                    val = int(match.group())
                    if val < self._minimum: val = self._minimum
                    if val > self._maximum: val = self._maximum
                    self._value = val
            except ValueError:
                pass
        self.update_text()

class Scheduler:
    def __init__(self, parent_widget, index):
        self.index = index
        self.checkBox_enable = QtWidgets.QPushButton(parent_widget)
        self.checkBox_enable.setObjectName(f"checkBox_enable_{index}")
        self.checkBox_enable.setCheckable(True)
        self.checkBox_enable.toggled.connect(self.update_enable_style)
        self.update_enable_style(False)

        self.spinBox_on_time = TouchSpinBox(parent_widget)
        self.spinBox_on_time.setMinimum(0)
        self.spinBox_on_time.setMaximum(10000)
        self.spinBox_on_time.setSingleStep(1)
        self.spinBox_on_time.setObjectName(f"spinBox_on_time_{index}")
        self.spinBox_on_time.setSuffix(" m")
        self.spinBox_on_time.setSpecialValueText("Default")
        self.spinBox_on_time.setFixedWidth(170)

        self.label_relay_state = QtWidgets.QLabel(parent_widget)
        self.label_relay_state.setObjectName(f"label_relay_state_{index}")
        self.label_relay_state.setAlignment(QtCore.Qt.AlignCenter)
        self.label_relay_state.setFixedWidth(80)
        self.label_relay_state.setFixedHeight(30)

        self.cycle_count = 0
        self.label_cycle_count = QtWidgets.QLabel(parent_widget)
        self.label_cycle_count.setObjectName(f"label_cycle_count_{index}")
        self.label_cycle_count.setAlignment(QtCore.Qt.AlignCenter)
        self.label_cycle_count.setFixedWidth(80)
        self.update_cycle_count_display()

        self.set_off_ui()

    def update_cycle_count_display(self):
        self.label_cycle_count.setText(str(self.cycle_count))

    def increment_cycle_count(self):
        self.cycle_count += 1
        self.update_cycle_count_display()

    def reset_cycle_count(self):
        self.cycle_count = 0
        self.update_cycle_count_display()

    def set_on_ui(self):
        self.label_relay_state.setText(" ON ")
        self.label_relay_state.setStyleSheet("QLabel { background-color : green; color : white; font-weight: bold; border-radius: 5px; }")

    def set_off_ui(self):
        self.label_relay_state.setText(" OFF ")
        self.label_relay_state.setStyleSheet("QLabel { background-color : red; color : white; font-weight: bold; border-radius: 5px; }")

    def update_enable_style(self, checked):
        if checked:
            self.checkBox_enable.setStyleSheet("QPushButton { background-color : green; color : white; font-weight: bold; }")
        else:
            self.checkBox_enable.setStyleSheet("QPushButton { background-color : red; color : white; font-weight: bold; }")

    def turn_on(self):
        RELAY.relayON(0, self.index)
        self.set_on_ui()

    def turn_off(self):
        RELAY.relayOFF(0, self.index)
        self.set_off_ui()

    def is_enabled(self):
        return self.checkBox_enable.isChecked()

    def get_on_time(self, default_time):
        val = self.spinBox_on_time.value()
        return val if val > 0 else default_time

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.checkBox_enable.setText(_translate("MainWindow", "Relay " + str(self.index)))
