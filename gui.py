import socket
import time
from _thread import *
import argparse

import keyboard
import numpy as np
import pyaudio
from PyQt5.QtCore import QBasicTimer, QThread, pyqtSignal, pyqtSlot

import client
import server

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMainWindow, QLabel, \
    QLineEdit, QGridLayout, QProgressBar, QMessageBox, QInputDialog


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
        print(sound_bytes)
        stream2.write(sound_bytes)
        stream2.stop_stream()
        stream2.close()
        self.p.terminate()
        print(f'저장된 녹음의 재생이 끝났습니다....')


    # 메소드 오버라이딩
    def send_audio(self, frames):
        self.frames = frames
        msg = np.array(self.frames).tobytes()
        self.client_socket.sendall(msg)
        time.sleep(1)
        self.client_socket.sendall(b'end')

        print('전송 완료....')

    #메소드 오버라이딩
    def receive_audio(self, device): # 오디오
        receive_stream = self.p.open(format=self.p.get_format_from_width(width=2), channels=1,
                                     rate=self.fs, output=True, output_device_index=device)

        receive_data = b''
        while True: # 송신받은 음성 재생
            data = self.client_socket.recv(1024)
            if data in b'end':
                receive_data = receive_data + data.rstrip(b'end')
                break
            receive_stream.write(data)

        receive_stream.stop_stream()
        receive_stream.close()
        self.p.terminate()

        print('Finished playback')





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
        self.listen_button = QPushButton('재생하기', self)
        self.transfer_button = QPushButton('전송하기', self)

        self.listen_button.setEnabled(False)
        self.transfer_button.setEnabled(False)
        self.record_button.setEnabled(False)

        hbox_button.addStretch(1)
        hbox_button.addWidget(self.record_button)
        hbox_button.addStretch(1)
        hbox_button.addWidget(self.listen_button)
        hbox_button.addStretch(1)

        self.record_button.clicked.connect(self.clicked_record)
        self.listen_button.clicked.connect(self.clicked_listen)
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
        main_layout.addWidget(self.transfer_button)
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

        self.record_button.setEnabled(True)

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

    #################################################################
    ################# 디바이스 선택 메소드 #########################
    def set_device(self, input):
        if input:
            items = self.AudioClient.set_input_device()
            if len(items) == 0:
                QMessageBox.critical(self, 'error','인식된 장치가 없습니다.', buttons=QMessageBox.Yes)
                return 0
            item_data, ok = QInputDialog.getItem(self, 'Set Input Device', '입력에 사용할 디바이스를 선택해주세요...', items)

            device_count = item_data.split(" ")[4]
            print(device_count)
        else:
            items = self.AudioClient.set_output_device()
            if len(items) == 0:
                QMessageBox.critical(self, 'error','인식된 장치가 없습니다.', buttons=QMessageBox.Yes)
                return 0
            item_data, ok = QInputDialog.getItem(self, 'Set Output Device', '출력에 사용할 디바이스를 선택해주세요...', items)

            device_count = item_data.split(" ")[4]
            print(device_count)
        if ok:
            return int(device_count)
    #####################################################
    ################# 녹음 이벤트 ############################

    def record_audio(self, input_device):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                             rate=16000, input=True, frames_per_buffer=1024,
                             input_device_index=input_device)

        self.frames = []
        print(f'Recode Starting')

        while True: # 시간 초를 정해두고 녹음 받음
            if keyboard.is_pressed('q'):
                break
            data = stream.read(self.chunk)
            self.frames.append(data)

        print(f'Recode Finishing')
        stream.stop_stream()
        stream.close()
        self.p.terminate()

    def clicked_record(self):
        self.frames = []

        device = self.set_device(True)
        if device == 0:
            return
        self.Record = RecordWindow(device)

        self.Record.buffer.connect(self.buffer)

        self.Record.start()
        finish = QMessageBox.information(self, 'Record', 'Recorded....', QMessageBox.SaveAll)
        self.Record.pause()

        print(len(self.frames))
        self.record_label.setText("녹음된 음성이 있습니다..")

        if len(self.frames) == 0:
            return
        else:
            self.listen_button.setEnabled(True)
            self.transfer_button.setEnabled(True)


    @pyqtSlot(bytes)
    def buffer(self, data):
        self.frames.append(data)
    ##################################################################

    ####################### 재생 이벤트 ###############################
    def clicked_listen(self):
        device = self.set_device(False)
        self.AudioClient.listening_audio(device, self.frames)
        QMessageBox.information(self, 'inform', '녹음된 음성이 모두 재생되었습니다....', QMessageBox.Yes)

    ##################################################################
    #
    # def clicked_transfer(self):
    #     self.AudioClient.send_audio(self.frames)




















class RecordWindow(QThread):
    buffer = pyqtSignal(bytes)

    def __init__(self, device):
        super().__init__()
        self.running = True
        self.device = device

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                        rate=16000, input=True, frames_per_buffer=1024,
                        input_device_index=self.device)

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



if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())