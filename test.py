import argparse

import numpy as np
import pyaudio
import wave
import time

from server import AudioServer
from client import AudioClient


def server_echo_test(port, ip):
    server = AudioServer(port, ip)

    conn, addr = server.server_socket.accept()
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
    print('echo test Finished')


def client_echo_test(port, ip):
    client = AudioClient(port, ip)

    while True:
        msg = input('서버로 보낼 메시지 : ')
        client.client_socket.sendall(msg.encode(encoding='utf-8'))
        data = client.client_socket.recv(1024)
        print('echo response : ', repr(data.decode()))
        if msg == 'end/':
            break

    print('echo test Finished')


def server_audio_test(port, ip):
    server = AudioServer(port, ip)
    conn, addr = server.server_socket.accept()
    print('connected by ', addr)

    server.server_socket.receive_audio(conn)
    print('수신 성공 .....')
    server.server_socket.send_audio(conn)
    print('송신 성공 ......')


def client_audio_test(port, ip): # 작업중...
    client = AudioClient(port, ip)

    while True:
        commend = input('명령어를 입력하세요 : ')
        if commend == 'end':
            break
        elif commend == 'record':
            try:
                client.record_audio()
            except:
                pass
        elif commend == 'listen':
            client.listening_audio()
        else:
            client.send_audio()
            print('오디오 전송 성공...')
            client.receive_audio()
            print('오디오 수신 성공....')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--user', required=True, help='서버와 클라이언트 중에 무엇을 실행시킬지 지정해주세요')
    parser.add_argument('--port', required=True, help='연결할 서버의 port번호를 지정해주세요.', default=28888) # server port : 28888
    parser.add_argument('--ip', required=True, help='연결할 서버의 IP 주소를 지정해주세요.') # server ip : 172.17.0.4

    args = parser.parse_args()

    port = int(args.port)
    ip = args.ip

    flag = input('test 항목을 설정하세요(echo, audio) : ')

    if args.user == 'client':
        if flag == 'echo':
            client_echo_test(port, ip)
        else:
            client_audio_test(port, ip)
    else:
        if flag == 'echo':
            server_echo_test(port, ip)
        else:
            server_audio_test(port, ip)


    print('테스트 종료합니다...')

