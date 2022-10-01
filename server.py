import socket
import time
from _thread import *
import argparse
import numpy as np
import wave
import pickle

import pyaudio


class AudioServer:

    def __init__(self, port, ip, chunk=1024, fs=16000, p=pyaudio.PyAudio):
        self.port = port
        self.ip = ip
        self.server_socket = self.socket_access(self.port, self.ip)
        self.chunk = chunk
        self.fs = fs
        self.frames = []
        self.p = p()

    def socket_access(self, port, ip):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)
        return server_socket

    def send_audio(self, conn):
        full_data = []
        with wave.open('arrive/file.wav', 'rb') as f:
            stream = self.p.open(format=self.p.get_format_from_width(f.getsampwidth()),
                                 channels=1,
                                 rate=self.fs,
                                 output=True
                                 )
            data = 1
            while data:
                data = f.readframes(self.chunk)
                conn.send(data)

    def receive_audio(self, conn): # 오디오를 받아서 저장
        msg_length = conn.recv(1024).decode()
        print(msg_length.decode())

        receive_data = b''

        for i in range(0, msg_length+1, 1024):
            data = conn.recv(1024)
            receive_data = receive_data + data
            print(i)

        print('여기까지 도착...1')
        full_data = pickle.loads(receive_data)

        print('여기까지 도착...2')
        self.frames = full_data['frames']

        print('여기까지 도착...3')
        print('전송 받은 프레임의 타입 : ', type(self.frames))

        # save the audio
        waveFile = wave.open('arrive/file.wav', 'wb')
        waveFile.setnchannels(1)
        waveFile.setsampwidth(full_data['sample_size'])
        waveFile.setframerate(self.fs)
        waveFile.writeframes(full_data['frames'])
        waveFile.close()

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

    def audio_test(self):
        conn, addr = self.server_socket.accept()
        print('connected by ', addr)

        self.receive_audio(conn)
        print('수신 성공 .....')
        # if self.frames.decode() == 'end':
        #     print('연결 종료....')
        #     return
        # else:
        self.send_audio(conn)
        print('송신 성공 ......')

        time.sleep(1)

