import pyaudio
import socket
import numpy as np
import pickle
import time

class AudioClient:

    def __init__(self, port, ip, chunk=1024, fs=16000, p=pyaudio.PyAudio):
        self.port = port
        self.ip = ip
        self.client_socket = self.socket_access(self.port, self.ip)
        self.chunk = 1024
        self.fs = 16000
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.input_device = None
        self.output_device = None

    def __del__(self):
        self.client_socket.close()

    def socket_access(self, port, ip):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        print('연결 준비 완료!!')
        return client_socket

    def set_input_device(self):
        audio = pyaudio.PyAudio()
        input_info = audio.get_host_api_info_by_index(0)
        input_device = input_info.get('deviceCount')
        for i in range(0, input_device):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " ‑ ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        self.input_device = int(input('녹음에 사용할 디바이스의 번호를 입력해주세요 : '))

    def set_output_device(self):
        audio = pyaudio.PyAudio()
        output_info = audio.get_host_api_info_by_index(0)
        output_device = output_info.get('deviceCount')
        for i in range(0, output_device):
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                print("Output Device id ", i, " ‑ ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

        self.output_device = int(input('재생에 사용할 디바이스의 번호를 입력해주세요 : '))


    def record_audio(self):
        self.set_input_device()
        print(f'Recode Starting')
        stream = self.p.open(format=pyaudio.paInt16, channels=1,
                             rate=16000, input=True, frames_per_buffer=1024,
                             input_device_index=self.input_device)

        for i in range(0, int(self.fs/self.chunk * 3)): # 시간 초를 정해두고 녹음 받음
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        self.p.terminate()

        print(f'Recode Finishing')

    def listening_audio(self):
        self.set_output_device()
        if len(self.frames) == 0:
            print('현재 저장된 녹음이 없습니다....')
            return 0
        else:
            sound = np.array(self.frames)
            sound_bytes = sound.tobytes()
            stream2 = self.p.open(format=self.p.get_format_from_width(width=2), channels=1,
                                  rate=self.fs, output=True,
                                  output_device_index=self.output_device)
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
            d = {
                'frames' : b''.join(self.frames),
                'sample_size' : pyaudio.get_sample_size(pyaudio.paInt16)
            }
            msg = pickle.dumps(d)
            self.client_socket.sendall(str(len(d['frames'])).encode(encoding='utf-8'))
            time.sleep(1)
            self.client_socket.send(msg)
            print('전송 완료....')


    def receive_audio(self): # 오디오
        receive_stream = self.p.open(format=self.p.get_format_from_width(width=2), channels=1, rate=self.fs, output=True)

        while True: # 송신받은 음성 재생
            data = self.client_socket.recv(1024)
            if data is None:
                break
            receive_stream.write(data)


        receive_stream.stop_stream()
        receive_stream.close()
        self.p.terminate()

        print('Finished playback')


    def echo_test(self):
        while True:
            msg = input('서버로 보낼 메시지 : ')
            self.client_socket.sendall(msg.encode(encoding='utf-8'))
            data = self.client_socket.recv(1024)
            print('echo response : ', repr(data.decode()))
            if msg == 'end/':
                break

    def audio_test(self): # 작업중...
        while True:
            commend = input('명령어를 입력하세요 : ')

            if commend == 'end':
                break
            if commend == 'record':
                try:
                    self.record_audio()
                except:
                    pass

            elif commend == 'listen':
                self.listening_audio()
            else:
                self.send_audio()
                print('오디오 전송 성공...')
                self.receive_audio()
                print('오디오 수신 성공....')


