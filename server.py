import socket
import time
from _thread import *
import argparse
import numpy as np
import wave
import pickle

import pyaudio


class Socket:

    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.socket_stream = self.socket_access(self.port, self.ip)
        self.chunk = 1024
        self.fs = 16000
        self.frames = []
        self.p = pyaudio.PyAudio

    def __del__(self):
        self.socket.close()

    def socket_access(self, port, ip):
        socket_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.socket_stream((self.ip, self.port))
        print('연결 준비 완료!!')
        return socket_stream


    def echo_test(self):
        while True:
            msg = input('서버로 보낼 메시지 : ')
            self.socket_stream.sendall(msg.encode(encoding='utf-8'))
            data = self.socket_stream.recv(1024)
            print('echo response : ', repr(data.decode()))
            if msg == 'end/':
                break


class AudioServer(Socket):

    def __init__(self, port, ip, chunk=1024, fs=16000, p=pyaudio.PyAudio):
        self.port = port
        self.ip = ip
        self.server_socket = self.socket_access(self.port, self.ip)
        self.chunk = chunk
        self.fs = fs
        self.frames = []
        self.p = p

    def socket_access(self, port, ip): # 오버라이딩
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)
        return server_socket

    def send_audio(self):
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
                self.server_socket.send(data)

    def receive_audio(self): # 오디오를 받아서 저장
        receive_data = b''
        while True:
            data = self.server_socket.recv(1024)
            if data is None:
                break
            receive_data = data + receive_data

        full_data = pickle.loads(receive_data)
        self.frames = full_data['frames']
        print('전송 받은 프레임의 타입 : ', type(self.frames))

        # save the audio
        waveFile =wave.open('arrive/file.wav', 'wb')
        waveFile.setchannels(1)
        waveFile.setsampwidth(full_data['sample_size'])
        waveFile.setframerate(self.fs)
        waveFile.writeframes(full_data['frames'])
        waveFile.close()

    def echo_test(self): # 오버라이딩
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

        self.receive_audio()
        print('수신 성공 .....')
        self.send_audio()
        print('송신 성공 ......')

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





        while True:
            commend = input('명령어를 입력하세요 : ')

            if commend == 'record':
                self.record_audio()
            elif commend == 'listen':
                self.listening_audio()
            else:
                self.send_audio()
                print('오디오 전송 성공...')
                self.receive_audio()

            if commend == 'end':
                break
