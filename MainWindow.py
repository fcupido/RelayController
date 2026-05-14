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

import os
from datetime import datetime
from PyQt5 import QtCore, QtWidgets
from scheduler import Scheduler, TouchSpinBox

class Ui_MainWindow(object):
    def __init__(self):
        self.schedulers = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.current_relay_index = -1
        self.time_remaining = 0
        self.log_file = "relays.log"

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Relay Controller")
        MainWindow.resize(800, 600)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        MainWindow.setWindowFlags(flags)

        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setStyleSheet("*{font-size: 13pt;}")

        self.layout = QtWidgets.QVBoxLayout(self.centralWidget)

        self.tabs = QtWidgets.QTabWidget()
        self.controllerTab = QtWidgets.QWidget()
        self.logsTab = QtWidgets.QWidget()

        self.tabs.addTab(self.controllerTab, "Controller")
        self.tabs.addTab(self.logsTab, "Logs")

        self.setupControllerTab()
        self.setupLogsTab()

        self.layout.addWidget(self.tabs)
        MainWindow.setCentralWidget(self.centralWidget)

        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

    def setupControllerTab(self):
        layout = QtWidgets.QVBoxLayout(self.controllerTab)

        # Global Settings
        settingsLayout = QtWidgets.QHBoxLayout()
        self.label_default_time = QtWidgets.QLabel("Default On-Time (m):")
        self.spinBox_default_time = TouchSpinBox()
        self.spinBox_default_time.setMinimum(1)
        self.spinBox_default_time.setMaximum(10000)
        self.spinBox_default_time.setValue(5)
        self.spinBox_default_time.setFixedWidth(170)

        self.btn_start = QtWidgets.QPushButton("Start Cycle")
        self.btn_start.clicked.connect(self.start_cycle)
        self.btn_stop = QtWidgets.QPushButton("Stop Cycle")
        self.btn_stop.clicked.connect(self.stop_cycle)
        self.btn_stop.setEnabled(False)

        settingsLayout.addWidget(self.label_default_time)
        settingsLayout.addWidget(self.spinBox_default_time)
        settingsLayout.addStretch()
        settingsLayout.addWidget(self.btn_start)
        settingsLayout.addWidget(self.btn_stop)

        layout.addLayout(settingsLayout)

        # Headers
        headerLayout = QtWidgets.QHBoxLayout()
        headerLayout.addWidget(QtWidgets.QLabel("Enable Relay"), 1)
        headerLayout.addWidget(QtWidgets.QLabel("On-Time (m)"), 0)
        headerLayout.addSpacing(40)
        headerLayout.addWidget(QtWidgets.QLabel("Status"), 0)
        headerLayout.addStretch()
        layout.addLayout(headerLayout)

        # Relays
        relay_scroll = QtWidgets.QScrollArea()
        relay_scroll.setWidgetResizable(True)
        relay_scroll_widget = QtWidgets.QWidget()
        self.relay_list_layout = QtWidgets.QVBoxLayout(relay_scroll_widget)

        for i in range(1, 8):
            sch = Scheduler(relay_scroll_widget, i)
            self.schedulers.append(sch)
            row = QtWidgets.QHBoxLayout()
            row.addWidget(sch.checkBox_enable, 1)
            row.addWidget(sch.spinBox_on_time, 0)
            row.addSpacing(20)
            row.addWidget(sch.label_relay_state, 0)
            row.addStretch()
            self.relay_list_layout.addLayout(row)

        self.relay_list_layout.addStretch()
        relay_scroll.setWidget(relay_scroll_widget)
        layout.addWidget(relay_scroll)

    def setupLogsTab(self):
        layout = QtWidgets.QVBoxLayout(self.logsTab)
        self.logViewer = QtWidgets.QPlainTextEdit()
        self.logViewer.setReadOnly(True)

        self.btn_refresh_logs = QtWidgets.QPushButton("Refresh Logs")
        self.btn_refresh_logs.clicked.connect(self.refresh_logs)

        layout.addWidget(self.logViewer)
        layout.addWidget(self.btn_refresh_logs)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Relay Controller"))
        for sch in self.schedulers:
            sch.retranslateUi()

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)
        self.refresh_logs()

    def refresh_logs(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    # For large logs, we might want to only show the last N lines
                    # but for now, reading all is what was requested.
                    self.logViewer.setPlainText(f.read())
                    self.logViewer.verticalScrollBar().setValue(self.logViewer.verticalScrollBar().maximum())
            except Exception as e:
                self.logViewer.setPlainText(f"Error reading logs: {e}")
        else:
            self.logViewer.setPlainText("No logs yet.")

    def start_cycle(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.current_relay_index = -1
        self.log("Cycle Started")
        self.next_relay()

    def stop_cycle(self):
        self.timer.stop()
        if self.current_relay_index != -1:
            sch = self.schedulers[self.current_relay_index]
            sch.turn_off()
            self.log(f"Relay {sch.index} turned OFF (Cycle Stopped)")

        self.current_relay_index = -1
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log("Cycle Stopped")
        self.statusBar.showMessage("Cycle Stopped")

    def next_relay(self):
        # Turn off current
        if self.current_relay_index != -1:
            sch = self.schedulers[self.current_relay_index]
            sch.turn_off()
            self.log(f"Relay {sch.index} turned OFF")

        # Find next enabled
        found = False
        num_schedulers = len(self.schedulers)
        start_search = self.current_relay_index + 1

        # Check from start_search to end
        for i in range(start_search, num_schedulers):
            if self.schedulers[i].is_enabled():
                self.current_relay_index = i
                found = True
                break

        if not found:
            # Wrap around: check from beginning
            for i in range(0, num_schedulers):
                 if self.schedulers[i].is_enabled():
                    self.current_relay_index = i
                    found = True
                    break

        if found:
            sch = self.schedulers[self.current_relay_index]
            self.time_remaining = sch.get_on_time(self.spinBox_default_time.value())
            sch.turn_on()
            self.log(f"Relay {sch.index} turned ON for {self.time_remaining} minutes")
            self.statusBar.showMessage(f"Relay {sch.index} active: {self.time_remaining}m left")
            self.timer.start(60000) # 1 minute tick
        else:
            self.stop_cycle()
            self.statusBar.showMessage("No enabled relays found.")

    def tick(self):
        self.time_remaining -= 1
        if self.time_remaining <= 0:
            self.next_relay()
        else:
            sch = self.schedulers[self.current_relay_index]
            self.statusBar.showMessage(f"Relay {sch.index} active: {self.time_remaining}m left")
