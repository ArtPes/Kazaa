# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setObjectName(_fromUtf8("MainWindow"))
        self.resize(1360, 450)
        self.setMaximumSize(QtCore.QSize(1360, 450))
        self.centralwidget = QtGui.QWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(1000, 1200))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setMaximumSize(QtCore.QSize(90, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.label_1 = QtGui.QLabel(self.centralwidget)
        self.label_1.setMaximumSize(QtCore.QSize(50, 20))
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.horizontalLayout.addWidget(self.label_1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.Panel = QtGui.QGridLayout()
        self.Panel.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.Panel.setObjectName(_fromUtf8("Panel"))
        self.client = QtGui.QTextBrowser(self.centralwidget)
        self.client.setMinimumSize(QtCore.QSize(300, 200))
        self.client.setMaximumSize(QtCore.QSize(1000, 1200))
        self.client.setObjectName(_fromUtf8("client"))
        self.Panel.addWidget(self.client, 1, 0, 1, 1)
        self.server = QtGui.QTextBrowser(self.centralwidget)
        self.server.setMinimumSize(QtCore.QSize(300, 200))
        self.server.setMaximumSize(QtCore.QSize(1000, 1200))
        self.server.setObjectName(_fromUtf8("server"))
        self.Panel.addWidget(self.server, 1, 1, 1, 1)
        self.gridLayout_3.addLayout(self.Panel, 0, 0, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_3)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "Peer", None))
        self.label_1.setText(_translate("MainWindow", "Server", None))

    def print_on_main_panel(self, message, color):
        if color == "10":
            self.server.setTextColor(QtGui.QColor('black'))
            self.server.append(message)
        elif color == "11":
            self.server.setTextColor(QtGui.QColor('red'))
            self.server.append(message)
        elif color == "12":
            self.server.setTextColor(QtGui.QColor('green'))
            self.server.append(message)
        elif color == "00":
            self.client.setTextColor(QtGui.QColor('black'))
            self.client.append(message)
        elif color == "01":
            self.client.setTextColor(QtGui.QColor('red'))
            self.client.append(message)
        elif color == "02":
            self.client.setTextColor(QtGui.QColor('green'))
            self.client.append(message)

'''
0 stampa sul terminale Client in nero
1 stampa sul terminale Client in rosso

10 stampa sul terminale Server in nero
11 stampa sul terminale Server in rosso
'''