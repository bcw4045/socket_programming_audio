import pyaudio
import socket
import numpy as np


class SocketClient:

    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.client_socket = self.socket_access(self.port, self.ip)
        self.chunk = 1024
        self.fs = 16000
        self.frames = []
        self.p = pyaudio.PyAudio

    def __del__(self):
        self.client_socket.close()

    def socket_access(self, port, ip):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        print('연결 준비 완료!!')
        return client_socket


    def echo_test(self):
        while True:
            msg = input('서버로 보낼 메시지 : ')
            self.client_socket.sendall(msg.encode(encoding='utf-8'))
            data = self.client_socket.recv(1024)
            print('echo response : ', repr(data.decode()))
            if msg == 'end/':
                break


class AudioModule(SocketClient):

    def __init__(self, port, ip, chunk=1024, fs=16000, p=pyaudio.PyAudio):
        super.__init__(port, ip)
        self.chunk = chunk
        self.fs = fs
        self.frames = []
        self.p = p

    def record_audio(self):
        print(f'Recode Starting')
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        for i in range(0, int(self.fs/self.chunk * 3)): # 시간 초를 정해두고 녹음 받음
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        self.p.terminate()

        print(f'Recode Finishing')

    def listening_audio(self):
        if len(self.frames) == 0:
            print('현재 저장된 녹음이 없습니다....')
            return 0
        else:
            sound = np.array(self.frames)

            sound_bytes = sound.tobytes()
            stream2 = self.p.open(format=self.p.get_format_from_width(width=2), channels=1, rate=self.fs, output=True)
            stream2.write(sound_bytes)
            stream2.stop_stream()
            stream2.close()
            self.p.terminate()
            print(f'저장된 녹음의 재생이 끝났습니다....')


    def send_audio(self):
        if len(self.frames) == 0:
            print('전송할 오디오가 없습니다...')
            self.record_audio()

        else:
            for i in range(0, len(self.frames), 1024):
                if (i + 1024) > len(self.frames):
                    data = self.frames[i:]
                else:
                    data = self.frames[i, i + 1024]
                self.client_socket.send_all(data)


    def receive_audio(self):
        receive_stream = self.p.open(format=self.p.get_format_from_width(width=2), channels=1, rate=self.fs, output=True)

        receive_data = []
        while True: # 송신받은 음성 재생
            data = self.client_socket.recv(1024)
            if data is None:
                break
            receive_data.append(data)
            receive_stream.write(data)


        receive_stream.stop_stream()
        receive_stream.close()
        self.p.terminate()

        print('Finished playback')

    def audio_test(self): # 작업중...
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
