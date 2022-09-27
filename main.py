# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import socket
from _thread import *
import argparse
import numpy as np
import pyaudio
import client
import server

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('user', required=True, help='서버와 클라이언트 중에 무엇을 실행시킬지 지정해주세요')
    parser.add_argument('--port', required=True, help='연결할 서버의 port번호를 지정해주세요.')
    parser.add_argument('--ip', required=True, help='연결할 서버의 IP 주소를 지정해주세요.')

    args = parser.parse_args()

    if args.user == 'client':
        client = client.SocketClient(args.port, args.ip)
        client.echo_test()
    else:
        server = server.SocketServer(args.port, args.ip)
        server.echo_test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
