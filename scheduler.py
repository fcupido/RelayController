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

class Scheduler:
    def __init__(self, parent_widget, index):
        self.index = index
        self.checkBox_enable = QtWidgets.QCheckBox(parent_widget)
        self.checkBox_enable.setObjectName(f"checkBox_enable_{index}")

        self.spinBox_on_time = QtWidgets.QSpinBox(parent_widget)
        self.spinBox_on_time.setMinimum(0)
        self.spinBox_on_time.setMaximum(10000)
        self.spinBox_on_time.setSingleStep(1)
        self.spinBox_on_time.setObjectName(f"spinBox_on_time_{index}")
        self.spinBox_on_time.setSuffix(" m")
        self.spinBox_on_time.setSpecialValueText("Default")
        self.spinBox_on_time.setFixedWidth(120)

        self.label_relay_state = QtWidgets.QLabel(parent_widget)
        self.label_relay_state.setObjectName(f"label_relay_state_{index}")
        self.label_relay_state.setAlignment(QtCore.Qt.AlignCenter)
        self.label_relay_state.setFixedWidth(80)
        self.label_relay_state.setFixedHeight(30)

        self.set_off_ui()

    def set_on_ui(self):
        self.label_relay_state.setText(" ON ")
        self.label_relay_state.setStyleSheet("QLabel { background-color : green; color : white; font-weight: bold; border-radius: 5px; }")

    def set_off_ui(self):
        self.label_relay_state.setText(" OFF ")
        self.label_relay_state.setStyleSheet("QLabel { background-color : red; color : white; font-weight: bold; border-radius: 5px; }")

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
