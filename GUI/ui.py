# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import random
import sys
import time
from PyQt4 import QtCore, QtGui

from GUI import main_window as MainWindow

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class MyThread(QtCore.QThread):
    print_trigger = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)

    def run(self):
        time.sleep(random.random()*5)  # random sleep to imitate working
        self.print_trigger.emit("prova", "mannaggia")

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    mainwindow = MainWindow.Ui_MainWindow()
    mainwindow.show()

    threads = []  # this will keep a reference to threads
    for i in range(10):
        thread = MyThread()  # create a thread
        thread.print_trigger.connect(mainwindow.print_on_main_panel)  # connect to it's signal
        thread.start()  # start the thread
        threads.append(thread)  # keep a reference

    sys.exit(app.exec_())