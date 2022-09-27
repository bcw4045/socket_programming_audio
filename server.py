import socket
import time
from _thread import *
import argparse
import numpy as np

import pyaudio


class SocketServer:

    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.server_socket = self.socket_access(self.port, self.ip)
        self.chunk = 1024
        self.fs = 16000
        self.frames = []
        self.p = pyaudio.PyAudio

    def __del__(self):
        self.server_socket.close()

    def socket_access(self, port, ip):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)
        return server_socket

    # def receive_audio(self):
    #     receive_stream = self.p.open(format=self.p.get_format_from_width(width=2), channels=1, rate=self.fs, output=True)
    #
    #     receive_data = []
    #     while True: # 송신 받은 음성 재생
    #        # if not data:
    #         #     break
    #         data = self.server_socket.recv(1024)
    #         receive_data.append(data)
    #
    #     receive_stream.stop_stream()
    #     receive_stream.close()
    #     self.p.terminate()
    #
    #     print('Finished playback')
    #
    # def send_audio(self): # 작업중....
    #     # send_stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.fs, input=True, frames_per_buffer=self.chunk)
    #     for i in range(0, len(self.frames), 1024) :
    #         if (i+1024) > len(self.frames):
    #             data = self.frames[i:]
    #         else:
    #             data = self.frames[i, i+1024]
    #         self.server_socket.send_all(data)
    #
    #     print('Finished playback')


    def echo_test(self):
        conn, addr = self.server_socket.accept()
        print('connected by ', addr)

        while True:
            data = conn.recv(1024)
            data = data.decode()
            print('받은 메시지 : ', data)
            msg = data + ' echo'
            conn.sendall(msg.encode(encoding='utf-8'))
            if data == 'end/':
                print('연결 종료...')
                break


        time.sleep(1)
