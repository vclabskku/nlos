### Reference
### https://seolin.tistory.com/98?category=762768 ###
### Socket programming Client code
from socket import *

class client():
    def __init__(self, port, host, recv_size=1024):
        self.port = port
        self.host = host
        self.recv_size = recv_size

        print("Preparing Client ...")
        self.clientSock = socket(AF_INET, SOCK_STREAM)
        self.clientSock.connect((self.host, self.port))
        print("Connected to Server!")

    def send_command(self, command):

        self.clientSock.send(command.encode('utf-8'))
        print(f"send data {command}")

        while True:
            recvData = self.clientSock.recv(self.recv_size).decode('utf-8')

            if recvData == 'rf_end':
                print(recvData)
                break

        return recvData