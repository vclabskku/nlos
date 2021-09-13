from socket import *
import time
import logging

class ServerCommand:
    def __init__(self, host, port, recv_size=1024, data_folder="./data"):
        self.port = port
        self.host = host
        self.recv_size = recv_size

        print("preparing server")
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print("server start")

        self.connectionSock, self.client_addr = self.sock.accept()

        print(f"{str(self.client_addr)} is connected")

        # self.connectionSock.send(f"folder-{data_folder}".encode('utf-8'))
        # print("set logging dir")

    def send_command(self, command):

        self.connectionSock.send(command.encode('utf-8'))
        print(f"send data {command}")

        while True:
            recvData = self.connectionSock.recv(1024).decode('utf-8')

            if recvData == 'rf_end':
                print(recvData)
                break

            if recvData == 'wave_end':
                print(recvData)
                break

            if "error" in recvData:
                raise ValueError("Error has been occurred on {}".format(recvData))

        return recvData


if __name__ == '__main__':

    host = "192.168.50.192"
    port = 8888
    server = ServerCommand(host, port)
    file_path = 'test2'
    while True:
        com = input("enter command (rf or wave) : ")
        if com == 'rf':
            recv = server.send_command('rf-{}'.format(file_path))
        elif com == 'wave':
            recv = server.send_command('wave-{}'.format(file_path))
        elif com == 'folder':
            recv = server.send_command('folder-{}'.format(file_path))
        else:
            print("wrong_command")
            continue

        # print(recv)
        # time.sleep(10)
