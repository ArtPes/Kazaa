from PyQt5 import QtCore, QtGui, QtWidgets

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setObjectName("MainWindow")
        self.resize(1360, 450)
        #self.setMaximumSize(QtCore.QSize(1360, 450))
        self.centralwidget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(1000, 1200))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setMaximumSize(QtCore.QSize(90, 20))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.label_1 = QtWidgets.QLabel(self.centralwidget)
        self.label_1.setMaximumSize(QtCore.QSize(50, 20))
        self.label_1.setObjectName("label_1")
        self.horizontalLayout.addWidget(self.label_1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.Panel = QtWidgets.QGridLayout()
        self.Panel.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.Panel.setObjectName("Panel")
        self.client = QtWidgets.QTextBrowser(self.centralwidget)
        self.client.setMinimumSize(QtCore.QSize(300, 200))
        self.client.setMaximumSize(QtCore.QSize(1000, 1200))
        self.client.setObjectName("client")
        self.Panel.addWidget(self.client, 1, 0, 1, 1)
        self.server = QtWidgets.QTextBrowser(self.centralwidget)
        self.server.setMinimumSize(QtCore.QSize(300, 200))
        self.server.setMaximumSize(QtCore.QSize(1000, 1200))
        self.server.setObjectName("server")
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
            self.server.setTextColor(QtGui.QColor('orange'))
            newfont = QtGui.QFont("Times", 11, QtGui.QFont.Bold)
            self.server.setFont(newfont)
            self.server.append(message)
        elif color == "11":
            self.server.setTextColor(QtGui.QColor('red'))
            newfont = QtGui.QFont("Times", 11, QtGui.QFont.Bold)
            self.server.setFont(newfont)
            self.server.append(message)
        elif color == "12":
            self.server.setTextColor(QtGui.QColor('green'))
            newfont = QtGui.QFont("Times", 11, QtGui.QFont.Bold)
            self.server.setFont(newfont)
            self.server.append(message)
        elif color == "00":
            self.client.setTextColor(QtGui.QColor('orange'))
            newfont = QtGui.QFont("Times", 11, QtGui.QFont.Bold)
            self.client.setFont(newfont)
            self.client.append(message)
        elif color == "01":
            self.client.setTextColor(QtGui.QColor('red'))
            newfont = QtGui.QFont("Times", 11, QtGui.QFont.Bold)
            self.client.setFont(newfont)
            self.client.append(message)
        elif color == "02":
            self.client.setTextColor(QtGui.QColor('green'))
            newfont = QtGui.QFont("Times", 11, QtGui.QFont.Bold)
            self.client.setFont(newfont)
            self.client.append(message)

'''
0 stampa sul terminale Client in blu
1 stampa sul terminale Client in rosso

10 stampa sul terminale Server in blu
11 stampa sul terminale Server in rosso
'''
