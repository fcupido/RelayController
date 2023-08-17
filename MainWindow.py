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
from scheduler import Scheduler
class Ui_MainWindow(object):
    def __init__(self):
        self.label_cycles_total = None
        self.label_time_on = None
        self.label_time_off = None
        self.sch0 = None
        self.sch6 = None
        self.sch5 = None
        self.sch4 = None
        self.sch3 = None
        self.sch2 = None
        self.statusBar = None
        self.sch1 = None
        self.centralWidget = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Relay Controller")

        MainWindow.resize(800, 600)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        MainWindow.setWindowFlags(flags)
        # MainWindow.showMaximized()

        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")

        self.centralWidget.setStyleSheet("*{font-size: 13pt;}")

        self.label_time_on = QtWidgets.QLabel(self.centralWidget)
        self.label_time_on.setGeometry(QtCore.QRect(140, 15, 141, 23))
        self.label_time_on.setObjectName("label_time_on")
        self.label_time_off = QtWidgets.QLabel(self.centralWidget)
        self.label_time_off.setGeometry(QtCore.QRect(310, 15, 131, 23))
        self.label_time_off.setObjectName("label_time_off")
        self.label_cycles_total = QtWidgets.QLabel(self.centralWidget)
        self.label_cycles_total.setGeometry(QtCore.QRect(480, 15, 191, 23))
        self.label_cycles_total.setObjectName("label_cycles_total")

        # create individual scheduler

        self.sch0 = Scheduler(self.centralWidget, 50, 1)
        self.sch1 = Scheduler(self.centralWidget, 126, 2)
        self.sch2 = Scheduler(self.centralWidget, 202, 3)
        self.sch3 = Scheduler(self.centralWidget, 278, 4)
        self.sch4 = Scheduler(self.centralWidget, 354, 5)
        self.sch5 = Scheduler(self.centralWidget, 430, 6)
        self.sch6 = Scheduler(self.centralWidget, 506, 7)

        MainWindow.setCentralWidget(self.centralWidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        # QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.sch0.retranslateUi()
        self.sch1.retranslateUi()
        self.sch2.retranslateUi()
        self.sch3.retranslateUi()
        self.sch4.retranslateUi()
        self.sch5.retranslateUi()
        self.sch6.retranslateUi()
        self.label_time_on.setText(_translate("MainWindow", "Time ON (m)"))
        self.label_time_off.setText(_translate("MainWindow", "Time OFF (m)"))
        self.label_cycles_total.setText(_translate("MainWindow", "Total Cycles"))

