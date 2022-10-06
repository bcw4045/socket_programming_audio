import socket
from _thread import *
import argparse
import numpy as np
import pyaudio
import client
import server

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel, \
    QLineEdit, QGridLayout


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Socket programming')

        main_layout = QGridLayout()

        self.setLayout(main_layout)

        ###### port, ip 입력하는 레이아웃

        port_label = QLabel('Port', self)
        ip_label = QLabel('Ip', self)

        port_line = QLineEdit(self)
        ip_line = QLineEdit(self)

        vbox = QVBoxLayout()
        vbox.addWidget(port_label)
        vbox.addWidget(port_line)

        vbox.addWidget(ip_label)
        vbox.addWidget(ip_line)

        ######################################

        conn_button = QPushButton('Connect', self)

        main_layout.addLayout(vbox, 0, 0)
        main_layout.addWidget(conn_button, 0, 1)


        # self. statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 300, 200)
        self.move(300, 300)
        self.resize(400, 200)
        self.show()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())