from PyQt5.QtWidgets import QFileDialog
from main import *
import sys
import base64
import binascii


class Panda(Ui_MainWindow):
    def __init__(self, window):
        self.setupUi(window)
        self.encodebutton.clicked.connect(self.encode)
        self.decodebutton.clicked.connect(self.decode)
        self.exitbutton.clicked.connect(self.sair)

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

            encoded, check = QFileDialog.getSaveFileName(directory='encodedfile.enc')
            if check:
                encoded = open(encoded, 'w')
                encoded = encoded.write(encode)
                print(encode)
                encoded.close()
                # Binary = binascii.a2b_uu(encode)
                # print(Binary)

    def decode(self):
        file, check = QFileDialog.getOpenFileName(directory='encodedfile.enc')
        if check:
            ficheiro = open(file, 'r')
            text = ficheiro.read()
            print(text)

            base64_bytes = text.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            decode = message_bytes.decode('ascii')

            # Ascii = binascii.b2a_uu(binary)
            # print(Ascii)

            decoded, check = QFileDialog.getSaveFileName(directory='decodedfile.txt')
            if check:
                print(decode)
                decoded = open(decoded, 'w')
                decoded = decoded.write(decode)
                decoded.close()

    def sair(self):

        quit()


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Panda(MainWindow)
MainWindow.show()
app.exec_()
