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
from PyQt5 import QtCore, QtWidgets, QtPrintSupport
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

        self.refresh_logs()
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
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(10)

        header_enable = QtWidgets.QLabel("Enable Relay")
        headerLayout.addWidget(header_enable, 1)

        header_ontime = QtWidgets.QLabel("On-Time (m)")
        header_ontime.setFixedWidth(170)
        header_ontime.setAlignment(QtCore.Qt.AlignCenter)
        headerLayout.addWidget(header_ontime, 0)

        header_cycles = QtWidgets.QLabel("Cycles")
        header_cycles.setFixedWidth(80)
        header_cycles.setAlignment(QtCore.Qt.AlignCenter)
        headerLayout.addWidget(header_cycles, 0)

        header_status = QtWidgets.QLabel("Status")
        header_status.setFixedWidth(80)
        header_status.setAlignment(QtCore.Qt.AlignCenter)
        headerLayout.addWidget(header_status, 0)

        headerLayout.addStretch()
        layout.addLayout(headerLayout)

        # Relays
        relay_scroll = QtWidgets.QScrollArea()
        relay_scroll.setWidgetResizable(True)
        relay_scroll_widget = QtWidgets.QWidget()
        self.relay_list_layout = QtWidgets.QVBoxLayout(relay_scroll_widget)
        self.relay_list_layout.setContentsMargins(0, 0, 0, 0)

        for i in range(1, 8):
            sch = Scheduler(relay_scroll_widget, i)
            self.schedulers.append(sch)
            row = QtWidgets.QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)
            row.addWidget(sch.checkBox_enable, 1)
            row.addWidget(sch.spinBox_on_time, 0)
            row.addWidget(sch.label_cycle_count, 0)
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

        buttonsLayout = QtWidgets.QHBoxLayout()

        self.btn_refresh_logs = QtWidgets.QPushButton("Refresh Logs")
        self.btn_refresh_logs.clicked.connect(self.refresh_logs)

        self.btn_clear_logs = QtWidgets.QPushButton("Clear Logs")
        self.btn_clear_logs.clicked.connect(self.clear_logs)

        self.btn_print_logs = QtWidgets.QPushButton("Print Logs")
        self.btn_print_logs.clicked.connect(self.print_logs)

        buttonsLayout.addWidget(self.btn_refresh_logs)
        buttonsLayout.addWidget(self.btn_clear_logs)
        buttonsLayout.addWidget(self.btn_print_logs)

        layout.addWidget(self.logViewer)
        layout.addLayout(buttonsLayout)

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
        log_exists = os.path.exists(self.log_file)
        log_empty = True
        if log_exists:
            try:
                file_size = os.path.getsize(self.log_file)
                log_empty = file_size == 0
                with open(self.log_file, "r") as f:
                    # If log is very large, only read the last 100KB to keep UI responsive
                    max_read = 100 * 1024
                    if file_size > max_read:
                        f.seek(file_size - max_read)
                        content = f.read()
                        # Ensure we don't start in the middle of a line
                        first_newline = content.find('\n')
                        if first_newline != -1:
                            content = "[...truncated...]\n" + content[first_newline+1:]
                    else:
                        content = f.read()

                    self.logViewer.setPlainText(content)
                    self.logViewer.verticalScrollBar().setValue(self.logViewer.verticalScrollBar().maximum())
            except Exception as e:
                self.logViewer.setPlainText(f"Error reading logs: {e}")
        else:
            self.logViewer.setPlainText("No logs yet.")

        if hasattr(self, 'btn_clear_logs'):
            self.btn_clear_logs.setEnabled(not log_empty)

    def clear_logs(self):
        if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dirname = os.path.dirname(self.log_file)
            basename = os.path.basename(self.log_file)
            name, ext = os.path.splitext(basename)
            new_basename = f"{name}_{timestamp}{ext}"
            new_filename = os.path.join(dirname, new_basename)

            os.rename(self.log_file, new_filename)
            # Create a new empty log file
            open(self.log_file, 'w').close()
            self.refresh_logs()

    def print_logs(self):
        printer = QtPrintSupport.QPrinter()
        dialog = QtPrintSupport.QPrintDialog(printer)
        if dialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            self.logViewer.print_(printer)

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
            self.log(f"Relay {sch.index} turned OFF (Cycle Stopped) - Cycle Count: {sch.cycle_count}")

        self.current_relay_index = -1
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log("Cycle Stopped")
        self.statusBar.showMessage("Cycle Stopped")

        for sch in self.schedulers:
            sch.reset_cycle_count()

    def next_relay(self):
        # Turn off current
        if self.current_relay_index != -1:
            sch = self.schedulers[self.current_relay_index]
            sch.turn_off()
            self.log(f"Relay {sch.index} turned OFF - Cycle Count: {sch.cycle_count}")

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
            sch.increment_cycle_count()
            sch.turn_on()
            self.log(f"Relay {sch.index} turned ON for {self.time_remaining} minutes - Cycle Count: {sch.cycle_count}")
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
