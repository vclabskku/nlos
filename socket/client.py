### Reference
### https://seolin.tistory.com/98?category=762768 ###
### Socket programming Client code
from socket import *
import threading
import time

class client():
    def __init__(self, port, host):
        self.port = port
        self.host = host

        self.clientSock = socket(AF_INET, SOCK_STREAM)
        self.clientSock.connect((self.host, self.port))
        self.receiver = threading.Thread(target=self.receive, args=(self.clientSock,))
        self.receiver.start()

    def receive(self, sock):
        while True:
            recvData = sock.recv(1024)
            print('상대방 :', recvData.decode('utf-8'))
            if recvData.decode('utf-8') == 'rf':
                self.execute(0)
                send_message = 'rf_end'
            elif recvData.decode('utf-8') == 'wave':
                self.execute(1)
                send_message = 'wave_end'

            sock.send(send_message.encode('utf-8'))

    def execute(self, flag):
        if flag == 0: ### RF execute
            print("execute RF")
        elif flag == 1: ### wave execute
            print("execute wave")

cli = client(8081, '192.168.50.174')