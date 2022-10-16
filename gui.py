import socket
import time
from _thread import *
import argparse

import PyQt5.QtCore
import keyboard
import numpy as np
import pyaudio
from PyQt5.QtCore import QBasicTimer, QThread, pyqtSignal, pyqtSlot

import client
import server

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel, \
    QLineEdit, QGridLayout, QProgressBar, QMessageBox, QInputDialog, QComboBox, QDialog


class Audio_Client(client.AudioClient):
    def __init__(self, port, ip):
        super().__init__(port, ip)

    # 메소드 오버라이딩
    def set_input_device(self):
        audio = pyaudio.PyAudio()
        input_info = audio.get_host_api_info_by_index(0)
        input_device = input_info.get('deviceCount')

        items = []
        for i in range(0, input_device):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                items.append(f"Input Device id  {i} ‑ {audio.get_device_info_by_host_api_device_index(0, i).get('name')}")
        return items

    #메소드 오버라이딩
    def set_output_device(self):
        audio = pyaudio.PyAudio()
        input_info = audio.get_host_api_info_by_index(0)
        input_device = input_info.get('deviceCount')

        items = []
        for i in range(0, input_device):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                items.append(
                    f"Input Device id  {i} ‑ {audio.get_device_info_by_host_api_device_index(0, i).get('name')}")
        return items

    # 메소드 오버라이딩
    def listening_audio(self, device, frames):
        sound = np.array(frames)
        sound_bytes = sound.tobytes()
        stream2 = self.p.open(format=self.p.get_format_from_width(width=2), channels=1,
                              rate=self.fs, output=True,
                              output_device_index=device)
        stream2.write(sound_bytes)
        stream2.stop_stream()
        stream2.close()
        self.p.terminate()
        print(f'저장된 녹음의 재생이 끝났습니다....')


    # 메소드 오버라이딩
    def send_audio(self, frames):
        self.client_socket.sendall(b'transfer')
        self.frames = frames
        msg = np.array(self.frames).tobytes()
        self.client_socket.sendall(msg)
        time.sleep(1)
        self.client_socket.sendall(b'end')

        print('전송 완료....')

    #메소드 오버라이딩
    def receive_audio(self): # 오디오
        receive_data = b''
        while True: # 송신받은 음성 재생
            data = self.client_socket.recv(1024)

            if data in b'end':
                receive_data = receive_data + data.rstrip(b'end')
                break
            receive_data += data
        return receive_data





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
        self.conn_button = QPushButton('Connect', self)
        self.disconn_button = QPushButton('Disconnect', self)
        self.disconn_button.setEnabled(False)

        self.conn_button.clicked.connect(self.clicked_connect)
        self.disconn_button.clicked.connect(self.clicked_disconn)

        vbox_button.addWidget(self.conn_button)
        vbox_button.addWidget(self.disconn_button)

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
        self.record_button = QPushButton('녹음하기', self)
        self.record_listen_button = QPushButton('녹음된 음성 재생', self)
        self.stop_button = QPushButton('정지하기', self)
        self.config = QPushButton('설정', self)

        self.record_button.setEnabled(False)
        self.record_listen_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        hbox_button.addStretch(1)
        hbox_button.addWidget(self.record_button)
        hbox_button.addStretch(1)
        hbox_button.addWidget(self.stop_button)
        hbox_button.addStretch(1)
        hbox_button.addWidget(self.record_listen_button)
        hbox_button.addStretch(1)
        hbox_button.addWidget(self.config)
        hbox_button.addStretch(1)

        self.stop_button.clicked.connect(self.clicked_stop)
        self.record_button.clicked.connect(self.clicked_record)
        self.record_listen_button.clicked.connect(self.clicked_listen)
        self.config.clicked.connect(self.config_device)
        ###########################################

        ########### 전송, 재생 버튼 ####################
        hbox2 = QHBoxLayout()
        self.transfer_button = QPushButton('전송하기', self)
        self.listen_button = QPushButton('재생하기', self)

        self.transfer_button.setEnabled(False)
        self.listen_button.setEnabled(False)
        self.config.setEnabled(False)

        self.transfer_button.clicked.connect(self.clicked_transfer)
        self.listen_button.clicked.connect(self.clicked_transfer_listen)

        hbox2.addStretch(1)
        hbox2.addWidget(self.transfer_button)
        hbox2.addStretch(1)
        hbox2.addWidget(self.listen_button)
        hbox2.addStretch(1)


        ############################################

        ############## progressbar #################
        # self.pbr = QProgressBar(self)
        # self.pbr.setValue(24)
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
        # main_layout.addWidget(self.pbr)
        # main_layout.addStretch(1)
        main_layout.addLayout(hbox2)
        main_layout.addStretch(1)
        main_layout.addLayout(status_layout)


        self.setGeometry(300, 300, 300, 200)
        self.move(300, 300)
        self.resize(500, 300)
        self.show()


    ############## 서버 연결 이벤트 ###################

    def clicked_connect(self): # 연결시에 이벤트 설정
        try:
            port = int(self.port_line.text())
            ip = self.ip_line.text()

        except:
            QMessageBox.critical(self, "QMessageBox", "잘못된 형식의 port와 ip입니다...")
            self.port_line.clear()
            self.ip_line.clear()
            return


        self.AudioClient = Audio_Client(port, ip)
        try:
            self.AudioClient.socket_access()
        except:
            QMessageBox.critical(self, "QMessageBox", "Port와 IP가 올바르지 않아 연결되지 않았습니다. 다시 연결해주세요...")
            self.port_line.clear()
            self.ip_line.clear()
            return

        self.conn_label.setText('Connected....')
        self.disconn_button.setEnabled(True)
        self.conn_button.setEnabled(False)
        self.config.setEnabled(True)

        return

    def clicked_disconn(self):
        self.AudioClient.__del__()
        self.port_line.clear()
        self.ip_line.clear()
        self.conn_label.setText('Disconnect....')
        self.disconn_button.setEnabled(False)
        self.conn_button.setEnabled(True)

        self.record_button.setEnabled(False)
        self.listen_button.setEnabled(False)
        self.transfer_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.record_listen_button.setEnabled(False)
        self.config.setEnabled(False)

        self.record_label.setText('없음...')

    #################################################################

    #####################################################

    def config_device(self):
        configwindow = ConfigWindow()

        configwindow.input_signal.connect(self.input_signal)
        configwindow.output_signal.connect(self.output_signal)

        # print('exec 전 : ', self.input_device)
        configwindow.exec_()
        if self.input_device == -1 and self.output_device == -1:
            QMessageBox.critical(self, 'error', '장치가 올바르게 설정되지 않았습니다...', QMessageBox.Yes)
        else:
            self.record_button.setEnabled(True)

    @pyqtSlot(int)
    def input_signal(self, text):
        self.input_device = text


    @pyqtSlot(int)
    def output_signal(self, text):
        self.output_device = text

    ################# 녹음 이벤트 ############################
    def clicked_record(self):
        self.frames = []
        self.stop = False

        print('device : ', self.input_device)
        self.Record = RecordWindow(self.input_device)

        self.Record.buffer.connect(self.buffer)

        self.Record.start()
        self.stop_button.setEnabled(True)
        self.record_button.setEnabled(False)
        self.record_listen_button.setEnabled(False)


    @pyqtSlot(bytes)
    def buffer(self, data):
        self.frames.append(data)
    ##################################################################
    ##################### 녹음 중지 이벤트 #############################
    def clicked_stop(self):
        self.Record.pause()
        self.stop_button.setEnabled(False)
        print(len(self.frames))
        self.record_label.setText("녹음된 음성이 있습니다..")

        if len(self.frames) == 0:
            QMessageBox.information(self, "녹음된 음성이 없습니다...")
            self.record_button.setEnabled(True)
            return
        else:
            self.record_listen_button.setEnabled(True)
            self.transfer_button.setEnabled(True)
        self.record_button.setEnabled(True)

    ####################### 재생 이벤트 ###############################
    def clicked_listen(self):
        device = self.output_device
        self.AudioClient.listening_audio(device, self.frames)
        QMessageBox.information(self, 'inform', '녹음된 음성이 모두 재생되었습니다....', QMessageBox.Yes)

    ##################################################################

    ###################### 전송 이벤트 ##############################

    def clicked_transfer(self):
        self.AudioClient.send_audio(self.frames)
        QMessageBox.information(self, '전송 알림', '전송이 완료되었습니다.....', QMessageBox.Yes)
        self.receive_data = self.AudioClient.receive_audio()
        print(len(self.receive_data))
        if len(self.receive_data) == 0:
            QMessageBox.critical(self, 'error', '전송 후 받은 파일이 없습니다....', QMessageBox.Yes)
        else:
            print('check')
            self.listen_button.setEnabled(True)
    ################################################################

    #################### 전송된 음성 재생 이벤트 #####################
    def clicked_transfer_listen(self):
        device = self.output_device
        self.AudioClient.listening_audio(device, self.receive_data)
        QMessageBox.information(self, 'inform', '전송 받은 음성이 모두 재생되었습니다....', QMessageBox.Yes)
    #############################################################


##### Record Thread와 Config Dialog ################


class RecordWindow(QThread):
    buffer = pyqtSignal(bytes)

    def __init__(self, device):
        super().__init__()
        self.running = True
        self.device = device

    def run(self):
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=pyaudio.paInt16, channels=1,
                            rate=16000, input=True, frames_per_buffer=1024,
                            input_device_index=self.device)
        except:
            print('error')
        while True: # 시간 초를 정해두고 녹음 받음
            if self.running == False:
                stream.stop_stream()
                stream.close()
                p.terminate()
                break
            data = stream.read(1024)
            self.buffer.emit(data)

    def pause(self):
        self.running = False


class ConfigWindow(QDialog):
    input_signal = PyQt5.QtCore.pyqtSignal(int)
    output_signal = PyQt5.QtCore.pyqtSignal(int)
    def __init__(self):
        super(ConfigWindow, self).__init__()
        self.initUI()
        self.input_device=-1
        self.output_device = -1

    def initUI(self):
        self.setWindowTitle('Device Configuration')

        input_items = self.set_device(True)
        output_items = self.set_device(False)

        main_layout = QVBoxLayout(self)
        input_layout = QHBoxLayout(self)
        output_layout = QHBoxLayout(self)

        input_label = QLabel("Input Device : ", self)
        output_label = QLabel("Output Device : ", self)


        self.input_combo = QComboBox(self)
        self.output_combo = QComboBox(self)

        self.input_combo.addItems(input_items)
        self.output_combo.addItems(output_items)

        self.input_combo.activated[str].connect(self.InputonActivated)
        self.output_combo.activated[str].connect(self.OutputonActivated)

        self.yes = QPushButton('Yes', self)


        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_combo)

        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_combo)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.yes)

        self.setLayout(main_layout)

        self.yes.clicked.connect(self.clicked_yes)
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def InputonActivated(self, text):
        self.input_combo.setCurrentText(text)


    def OutputonActivated(self, text):
        self.output_combo.setCurrentText(text)


    def clicked_yes(self):
        output_device = self.output_combo.currentText()
        self.output_device = int(output_device.split(' ')[4])
        self.output_signal.emit(self.output_device)

        input_device = self.input_combo.currentText()
        self.input_device = int(input_device.split(' ')[4])
        self.input_signal.emit(self.input_device)

        self.close()

    def closeEvent(self, QCloseEvent): # real signature unknown; restored from __doc__
        if self.input_device == -1 and self.output_device == -1:
            self.input_signal.emit(-1)
            self.output_signal.emit(-1)


    def set_input_device(self):
        audio = pyaudio.PyAudio()
        input_info = audio.get_host_api_info_by_index(0)
        input_device = input_info.get('deviceCount')

        items = []
        for i in range(0, input_device):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                items.append(f"Input Device id  {i} ‑ {audio.get_device_info_by_host_api_device_index(0, i).get('name')}")
        return items

    #메소드 오버라이딩
    def set_output_device(self):
        audio = pyaudio.PyAudio()
        input_info = audio.get_host_api_info_by_index(0)
        input_device = input_info.get('deviceCount')

        items = []
        for i in range(0, input_device):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                items.append(
                    f"Input Device id  {i} ‑ {audio.get_device_info_by_host_api_device_index(0, i).get('name')}")
        return items

    def set_device(self, input):
        if input:
            items = self.set_input_device()
            return items
        else:
            items = self.set_output_device()
            return items

###################################################################

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())