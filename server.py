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

    def __del__(self):
        self.server_socket.close()

    def socket_access(self, port, ip):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)
        return server_socket

    def send_audio(self, conn):
        full_data = []
        with wave.open('arrive/file.wav', 'rb') as f:
            data = 1
            while data:
                data = f.readframes(self.chunk)
                conn.send(data)

        time.sleep(1)
        conn.sendall(b'end')

    def receive_audio(self, conn): # 오디오를 받아서 저장
        receive_data = b''

        while True:
            data = conn.recv(1024)
            if data == b'end':
                break
            receive_data = receive_data + data

        full_data = pickle.loads(receive_data)

        self.frames = full_data['frames']

        print('전송 받은 프레임의 타입 : ', type(self.frames))

        # save the audio
        waveFile = wave.open('arrive/file.wav', 'wb')
        waveFile.setnchannels(1)
        waveFile.setsampwidth(full_data['sample_size'])
        waveFile.setframerate(self.fs)
        waveFile.writeframes(full_data['frames'])
        waveFile.close()

    def run(self):
        conn, addr = self.server_socket.accept()
        while True:
            try:
                commend = conn.recv(1024).decode()
                print('전송 받은 명령어 : ', commend)
                if commend == 'end':
                    conn.shutdown()
                elif commend == 'testaudio':
                    print('진입 성공...')
                    self.receive_audio(conn)
                    print('수신 성공 .....')
                    self.send_audio(conn)
                    print('송신 성공 ......')
                else:
                    continue
            except:
                conn, addr = self.server_socket.accept()
