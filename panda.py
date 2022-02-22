import base64
import sys
import bitstruct
import bitarray
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QFileDialog, QSlider

from main import *


class Panda(Ui_MainWindow):
    def __init__(self, window, vSl=1):
        self.setupUi(window)
        self.encodebutton.clicked.connect(self.encode)
        self.decodebutton.clicked.connect(self.decode)
        self.exitbutton.clicked.connect(self.sair)
        self.max_sliding_window_size = QSlider(Qt.Horizontal)
        self.max_sliding_window_size.setValue(vSl)
        self.max_sliding_window_size.setMinimum(1)
        self.max_sliding_window_size.setMaximum(4096)
        self.max_sliding_window_size.setTickPosition(QSlider.TicksBelow)
        self.max_sliding_window_size.setTickInterval(10)
        self.max_sliding_window_size.valueChanged[int].connect(self.valuechange)
        vSl = self.max_sliding_window_size.value()
        print("__init__vSl -> ", vSl)

    def valuechange(self, value):
        self.max_sliding_window_size = self.max_sliding_window_size.value()
        self.max_sliding_window_size.__init__(value)
        return self.max_sliding_window_size

    def sair(self):

        quit()

    def encode(self):

        file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                  "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)")
        if check:
            ficheiro = open(file, 'r')
            text = ficheiro.read()
            print(text)

            text1 = text.encode('ascii')
            base64_bytes = base64.b64encode(text1)
            encode = base64_bytes.decode('ascii')

            print(encode)

            byte_array = encode.encode()

            binary_int = int.from_bytes(byte_array, sys.byteorder)

            binary_string = bin(binary_int)
            byt = binary_string.encode('utf-8')
            print(byt)

            encoded, check = QFileDialog.getSaveFileName(directory='encoded.ascii')
            if check:
                encoded = open(encoded, 'w')
                encoded.write(encode)

                binary, check = QFileDialog.getSaveFileName(directory='encoded.bin')
                if check:
                    binary = open(binary, 'wb')

                    binary.write(byt)

    def decode(self):
        file, check = QFileDialog.getOpenFileName(directory='encoded.ascii')
        if check:
            ficheiro = open(file, 'r')
            text = ficheiro.read()

        decoded, check = QFileDialog.getSaveFileName(directory='decodedascii.txt')
        if check:
            decoded = open(decoded, 'w')
            base64_message = text.tostring()
            base64_bytes = base64_message.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('ascii')
            decoded.write(message)

        openbin, check = QFileDialog.getOpenFileName(directory='encoded.bin')
        if check:
            openbin = open(openbin, 'rb')
            bites = openbin.read()

        binary, check = QFileDialog.getSaveFileName(directory='decodedbin.txt')
        if check:
            binary = open(binary, 'w')
            decodedbin = bites.decode('ascii')
            binary.write(decodedbin)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Panda(MainWindow)
    MainWindow.show()
    app.exec_()
