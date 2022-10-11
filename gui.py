import socket
from _thread import *
import argparse
import numpy as np
import pyaudio
from PyQt5.QtCore import QBasicTimer

import client
import server

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel, \
    QLineEdit, QGridLayout, QProgressBar, QMessageBox


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Socket programming')

        # self.statusBar().showMessage('Disconnect...')

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        ###### port, ip 입력하는 레이아웃
        port_label = QLabel('Port', self)
        ip_label = QLabel('Ip', self)

        self.port_line = QLineEdit(self)
        self.ip_line = QLineEdit(self)

        vbox_label = QVBoxLayout()
        vbox_label.addWidget(port_label)
        vbox_label.addWidget(self.port_line)

        vbox_label.addWidget(ip_label)
        vbox_label.addWidget(self.ip_line)

        ##################################################

        ############### connect/disconnect layout ###############

        vbox_button = QVBoxLayout()
        conn_button = QPushButton('Connect', self)
        disconn_button = QPushButton('Disconnect', self)
        disconn_button.setEnabled(False)

        vbox_button.addWidget(conn_button)
        vbox_button.addWidget(disconn_button)

        ######################################################

        ############ 상단 레이아웃 ###############
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addLayout(vbox_label)
        top_layout.addStretch(2)
        top_layout.addLayout(vbox_button)
        top_layout.addStretch(1)

        #########################################

        ####### 녹음, 음성, 전송 버튼 생성 ###########
        hbox_button = QHBoxLayout()
        record_button = QPushButton('녹음하기', self)
        listen_button = QPushButton('재생하기', self)
        transfer_button = QPushButton('전송하기', self)

        listen_button.setEnabled(False)
        transfer_button.setEnabled(False)

        hbox_button.addStretch(1)
        hbox_button.addWidget(record_button)
        hbox_button.addStretch(1)
        hbox_button.addWidget(listen_button)
        hbox_button.addStretch(1)

        ###########################################

        ############## progressbar #################
        self.pbr = QProgressBar(self)
        self.pbr.setValue(24)
        # self.timer = QBasicTimer()
        # self.finished = False
        ###########################################

        ############ 상태 라벨 추가 ############
        status_layout = QVBoxLayout()

        conn_layout = QHBoxLayout()
        self.conn_status = QLabel('연결 상태 -> ', self)
        self.conn_label = QLabel('Disconnect....', self)


        record_layout = QHBoxLayout()
        self.record_status = QLabel('현재 녹음된 음성 -> ', self)
        self.record_label = QLabel('없음...', self)

        conn_layout.addWidget(self.conn_status)
        conn_layout.addWidget(self.conn_label)

        record_layout.addWidget(self.record_status)
        record_layout.addWidget(self.record_label)

        status_layout.addLayout(conn_layout)
        status_layout.addLayout(record_layout)
        #######################################


        main_layout.addLayout(top_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(hbox_button)
        main_layout.addStretch(1)
        main_layout.addWidget(self.pbr)
        main_layout.addStretch(1)
        main_layout.addWidget(transfer_button)
        main_layout.addStretch(1)
        main_layout.addLayout(status_layout)


        self.setGeometry(300, 300, 300, 200)
        self.move(300, 300)
        self.resize(500, 300)
        self.show()

    def clicked_connect(self): # 연결시에 이벤트 설정
        port = self.port_line.text()
        ip = self.ip_line.text()

        self.AudioClient = client.AudioClient(port, ip)
        try:
            self.AudioClient.socket_access()
        except:
            QMessageBox.critical(self, "QMessageBox", "Port와 IP가 올바르지 않아 연결되지 않았습니다. 다시 연결해주세요...")
            self.port_line.clear()
            self.ip_line.clear()
            return


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())