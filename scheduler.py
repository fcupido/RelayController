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
from PyQt5.QtCore import QTimer
import piplates.RELAYplate as RELAY

class Scheduler:
    def __init__(self, central_widget, y_coordinate, index):
        self.index = index
        self.checkBox_enable = QtWidgets.QCheckBox(central_widget)
        self.checkBox_enable.setGeometry(QtCore.QRect(30, y_coordinate, 161, 40))
        self.checkBox_enable.setObjectName("checkBox_enable")
        self.spinBox_on_time = QtWidgets.QSpinBox(central_widget)
        self.spinBox_on_time.setGeometry(QtCore.QRect(120, y_coordinate, 140, 60))
        self.spinBox_on_time.setMinimum(0)
        self.spinBox_on_time.setMaximum(10000)
        self.spinBox_on_time.setSingleStep(5)
        self.spinBox_on_time.setObjectName("spinBox_on_time")

        self.spinBox_off_time = QtWidgets.QSpinBox(central_widget)
        self.spinBox_off_time.setGeometry(QtCore.QRect(290, y_coordinate, 140, 60))
        self.spinBox_off_time.setMinimum(0)
        self.spinBox_off_time.setMaximum(10000)
        self.spinBox_off_time.setSingleStep(5)
        self.spinBox_off_time.setObjectName("spinBox_off_time")
        self.spinBox_cycles_left = QtWidgets.QSpinBox(central_widget)
        self.spinBox_cycles_left.setGeometry(QtCore.QRect(460, y_coordinate, 141, 60))
        self.spinBox_cycles_left.setMinimum(-1)
        self.spinBox_cycles_left.setMaximum(100000)
        self.spinBox_cycles_left.setSingleStep(1000)
        self.spinBox_cycles_left.setObjectName("spinBox_cycles_left")

        self.label_relay_state = QtWidgets.QLabel(central_widget)
        self.label_relay_state.setGeometry(QtCore.QRect(620, y_coordinate, 40, 23))
        self.label_relay_state.setObjectName("label_relay_state")
        self.label_relay_state.setStyleSheet("QLabel { background-color : red; color : black; }")

        self.label_cycles_completed = QtWidgets.QLabel(central_widget)
        self.label_cycles_completed.setGeometry(QtCore.QRect(680, y_coordinate, 141, 23))
        self.label_cycles_completed.setObjectName("label_cycles_completed")
        self.label_cycles_completed.setText("Cycles: 0")

        self.spinBox_on_time.setEnabled(False)
        self.spinBox_off_time.setEnabled(False)
        self.spinBox_cycles_left.setEnabled(False)

        self.enabled = False  # whether the relay can be turned on
        self.relay_power = False  # whether the relay is ON

        self.checkBox_enable.stateChanged.connect(self.on_check_box_enable_state_changed)
        self.spinBox_on_time.valueChanged.connect(self.spin_box_on_time_value_changed)
        self.spinBox_off_time.valueChanged.connect(self.spin_box_off_time_value_changed)
        self.spinBox_cycles_left.valueChanged.connect(self.spin_box_cycles_left_value_changed)
        self.on_time = 0
        self.off_time = 0
        self.time_left = 0
        self.cycles_left = 0
        self.cycles_completed = 0
        self.on_state = True  # whether we are on the ON cycle or the OFF cycle
        self.current_relay_state = False
        self.changeRelayPower()
        self.valid_config = False

        self.timer = QTimer(central_widget)
        self.timer.timeout.connect(self.on_timeout)

    def update_ui(self):
        pass

    def on_timeout(self):
        self.time_left -= 1
        if not self.time_left > 0:
            if self.on_state:
                self.on_state = not self.off_time > 0
                if self.cycles_left > 0:
                    self.cycles_left -= 1  # -1 is no-stop
                    self.cycles_completed += 1
            else:
                self.on_state = True

            if self.on_state:
                self.time_left = self.on_time
            else:
                self.time_left = self.off_time
            self.label_cycles_completed.setText("Cycles: " + str(self.cycles_completed))
        # self.label_time_left.setText("Time left: " + str(self.time_left))
        self.evaluate_config()

    def evaluate_relay_state(self):
        new_relay_state = self.enabled and self.valid_config and self.on_state
        if self.current_relay_state != new_relay_state:
            self.current_relay_state = new_relay_state
            self.changeRelayPower()

    def evaluate_config(self):
        new_valid_config = self.cycles_left != 0 and self.enabled and self.on_time > 0

        if new_valid_config and not self.valid_config:
            self.valid_config = True
            self.timer.start(60000)
        elif not new_valid_config and self.valid_config:
            self.valid_config = False
            self.timer.stop()
        self.evaluate_relay_state()

    def spin_box_on_time_value_changed(self, value):
        self.on_time = value
        if self.on_state:
            self.time_left = self.on_time
            # self.label_time_left.setText("Time left: " + str(self.time_left))
        self.evaluate_config()

    def spin_box_off_time_value_changed(self, value):
        self.off_time = value
        if not self.on_state:
            self.time_left = self.off_time
            # self.label_time_left.setText("Time left: " + str(self.time_left))
        self.evaluate_config()

    def spin_box_cycles_left_value_changed(self, value):
        self.cycles_left = value
        self.label_cycles_completed.setText("Cycles: " + str(self.cycles_completed))
        self.evaluate_config()

    def changeRelayPower(self):
        # print("Turning relay: " + str(self.index) + " to state: " + str(self.current_relay_state))
        if self.current_relay_state:
            RELAY.relayON(0, self.index)
            self.label_relay_state.setText(" ON ")
            self.label_relay_state.setStyleSheet("QLabel { background-color : green; color : black; }")
        else:
            RELAY.relayOFF(0, self.index)
            self.label_relay_state.setText(" OFF ")
            self.label_relay_state.setStyleSheet("QLabel { background-color : red; color : black; }")

    # Whether the scheduler row is active
    def on_check_box_enable_state_changed(self):
        state = self.checkBox_enable.checkState()
        self.enabled = state == QtCore.Qt.CheckState.Checked
        self.spinBox_on_time.setEnabled(self.enabled)
        self.spinBox_off_time.setEnabled(self.enabled)
        self.spinBox_cycles_left.setEnabled(self.enabled)
        if not self.enabled:
            self.spinBox_on_time.setValue(0)
            self.spinBox_off_time.setValue(0)
            self.spinBox_cycles_left.setValue(0)
        self.evaluate_config()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.checkBox_enable.setText(_translate("MainWindow", "Relay: " + str(self.index)))

