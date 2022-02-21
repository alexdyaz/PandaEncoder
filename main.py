from PyQt5 import QtCore, QtGui, QtWidgets

from resources import icon_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(770, 380)
        MainWindow.setMinimumSize(QtCore.QSize(770, 380))
        MainWindow.setMaximumSize(QtCore.QSize(770, 380))
        MainWindow.setStyleSheet("background-repeat: no-repeat;\n"
                                 "background-image: url(:/icon/fundo.png);\n"
                                 "background-position: center;")
        MainWindow.setIconSize(QtCore.QSize(64, 64))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.encodebutton = QtWidgets.QPushButton(self.centralwidget)
        self.encodebutton.setGeometry(QtCore.QRect(40, 50, 111, 91))
        self.encodebutton.setStyleSheet("image: url(:/icon/encode.png);")
        self.encodebutton.setText("")
        self.encodebutton.setObjectName("encodebutton")
        self.decodebutton = QtWidgets.QPushButton(self.centralwidget)
        self.decodebutton.setGeometry(QtCore.QRect(180, 50, 111, 91))
        self.decodebutton.setStyleSheet("image: url(:/icon/decode.png);")
        self.decodebutton.setText("")
        self.decodebutton.setObjectName("decodebutton")
        self.exitbutton = QtWidgets.QPushButton(self.centralwidget)
        self.exitbutton.setGeometry(QtCore.QRect(680, 10, 71, 61))
        self.exitbutton.setStyleSheet("image: url(:/icon/exit.png);")
        self.exitbutton.setText("")
        self.exitbutton.setObjectName("exitbutton")
        self.encodelabel = QtWidgets.QLabel(self.centralwidget)
        self.encodelabel.setGeometry(QtCore.QRect(60, 150, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Historic")
        font.setPointSize(16)
        self.encodelabel.setFont(font)
        self.encodelabel.setStyleSheet("color: rgb(255, 255, 255);\n"
                                       "background-color: #ffffff;\n"
                                       "opacity: 3;\n"
                                       "")
        self.encodelabel.setLineWidth(0)
        self.encodelabel.setObjectName("encodelabel")
        self.decodelabel = QtWidgets.QLabel(self.centralwidget)
        self.decodelabel.setGeometry(QtCore.QRect(200, 150, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Historic")
        font.setPointSize(16)
        self.decodelabel.setFont(font)
        self.decodelabel.setAutoFillBackground(False)
        self.decodelabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.decodelabel.setObjectName("decodelabel")
        self.max_sliding_window_size = QtWidgets.QSlider(self.centralwidget)
        self.max_sliding_window_size.setGeometry(QtCore.QRect(40, 220, 251, 22))
        self.max_sliding_window_size.setStyleSheet("selection-background-color: rgb(85, 255, 255);")
        self.max_sliding_window_size.setOrientation(QtCore.Qt.Horizontal)
        self.max_sliding_window_size.setObjectName("max_sliding_window_size")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(130, 240, 161, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono NL")
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("alternate-background-color: rgb(255, 255, 255);")
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionEncode = QtWidgets.QAction(MainWindow)
        self.actionEncode.setObjectName("actionEncode")
        self.actionDecode = QtWidgets.QAction(MainWindow)
        self.actionDecode.setObjectName("actionDecode")
        self.actionSair = QtWidgets.QAction(MainWindow)
        self.actionSair.setObjectName("actionSair")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PandaEncoder"))
        self.encodelabel.setText(_translate("MainWindow", "Encode"))
        self.decodelabel.setText(_translate("MainWindow", "Decode"))
        self.label.setText(_translate("MainWindow", "Compression Level"))
        self.actionEncode.setText(_translate("MainWindow", "Encode"))
        self.actionDecode.setText(_translate("MainWindow", "Decode"))
        self.actionSair.setText(_translate("MainWindow", "Exit"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
